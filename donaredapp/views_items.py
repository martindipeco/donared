from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Item, Categoria
from .services.item_service import ItemService
from .forms import ItemForm
import os

@login_required
def publicar(request):
    if request.method == "POST":
        # delegamos en service para la lógica de negocio
        item_service = ItemService()
        result = item_service.crear_item(request.POST, files=request.FILES, user=request.user)
        
        if result['success']:
            messages.success(request, "¡Item publicado con éxito!")
            return redirect("donaredapp:tarjeta", item_id=result['item'].id)
        else:
            # Return errors from the service
            messages.error(request, result['error'])
            # Return to form with entered data
            categorias = Categoria.objects.all()
            context = {
                "categorias": categorias,
                'MAX_IMAGE_SIZE_MB': settings.MAX_IMAGE_SIZE_MB,
                'MAX_IMAGE_SIZE_BYTES': settings.MAX_IMAGE_SIZE_BYTES,
                "form_data": request.POST,  # Pass back the form data
            }
            return render(request, "donaredapp/publicar.html", context)
    
    #asumiendo que el método es GET
    else:
        categorias = Categoria.objects.all()
        context = {
            "categorias": categorias,
        }
        return render(request, "donaredapp/publicar.html", context)
    
@login_required
def editar_item(request, item_id):
    try:
        # Try to get the item, but specifically check user ownership
        item = get_object_or_404(Item, pk=item_id)
        
        # Check if the current user is the owner of the item
        if request.user != item.usuario:
            messages.error(request, "No tienes permiso para editar este ítem.")
            return redirect('donaredapp:index')
        
        # Get the lists needed for the form dropdowns
        categorias = Categoria.objects.all()

        # Create a context dictionary with the item data to pre-populate the form
        context = {
            'item': item,
            'categorias': categorias,
            'editing': True,  # Flag to indicate we're editing, not creating new
            'MAX_IMAGE_SIZE_MB': settings.MAX_IMAGE_SIZE_MB,  # For the JavaScript alert
        }

        return render(request, 'donaredapp/publicar.html', context)
    
    except Item.DoesNotExist:
        # Handle case where item doesn't exist
        messages.error(request, "El ítem que intentas editar no existe.")
        return redirect('donaredapp:index')

@login_required
def actualizar_item(request, item_id):
    """
    View to process the item update form submission.
    """
    item = get_object_or_404(Item, pk=item_id)
    if request.user != item.usuario:
        messages.error(request, "No tienes permiso para editar este ítem.")
        return redirect('donaredapp:index')
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        mantener_imagen = request.POST.get('mantener_imagen')
        nueva_imagen = request.FILES.get('imagen')
        imagen_error = False
        old_image_path = item.imagen.path if item.imagen else None
        # Validar tamaño de imagen antes de guardar el formulario
        if nueva_imagen:
            if nueva_imagen.size > settings.MAX_IMAGE_SIZE_BYTES:
                messages.error(request, f"La imagen no debe exceder {settings.MAX_IMAGE_SIZE_MB} MB.")
                imagen_error = True
        if not imagen_error and form.is_valid():
            try:
                item = form.save()
                # Si el usuario desmarcó mantener_imagen y no subió una nueva, eliminar la imagen
                if not mantener_imagen and not nueva_imagen and item.imagen:
                    if old_image_path and os.path.isfile(old_image_path):
                        os.remove(old_image_path)
                    item.imagen = None
                    item.save()
                messages.success(request, "¡Ítem actualizado con éxito!")
                return redirect('donaredapp:tarjeta', item_id=item.id)
            except Exception as e:
                messages.error(request, f"Error al actualizar el ítem: {str(e)}")
                return redirect('donaredapp:editar_item', item_id=item_id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'categoria':
                        messages.error(request, "La categoría seleccionada no existe")
                    else:
                        messages.error(request, f"{field}: {error}")
            return redirect('donaredapp:editar_item', item_id=item_id)
    return redirect('donaredapp:editar_item', item_id=item_id)

@login_required
def ocultar_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id, usuario=request.user)

    # Check if the current user is the owner of the item
    if request.user != item.usuario:
        messages.error(request, "No tienes permiso para dar de baja este ítem.")
        return redirect('donaredapp:index')
    item.activo = False
    item.save()
    messages.success(request, "¡Item ocultado con éxito!")
    return redirect("donaredapp:index")