from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Item, Zona, Categoria
from .services.item_service import ItemService
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
            zonas = Zona.objects.all()
            categorias = Categoria.objects.all()
            context = {
                "zonas": zonas,
                "categorias": categorias,
                'MAX_IMAGE_SIZE_MB': settings.MAX_IMAGE_SIZE_MB,
                'MAX_IMAGE_SIZE_BYTES': settings.MAX_IMAGE_SIZE_BYTES,
                "form_data": request.POST,  # Pass back the form data
            }
            return render(request, "donaredapp/publicar.html", context)
    
    #asumiendo que el método es GET
    else:
        zonas = Zona.objects.all()
        categorias = Categoria.objects.all()
        context = {
            "zonas": zonas,
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
        zonas = Zona.objects.all()
        categorias = Categoria.objects.all()

        # Create a context dictionary with the item data to pre-populate the form
        context = {
            'item': item,
            'zonas': zonas,
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
    # Get the item or return 404 if not found
    item = get_object_or_404(Item, pk=item_id)
    
    # Check if the current user is the owner of the item
    if request.user != item.usuario:
        messages.error(request, "No tienes permiso para editar este ítem.")
        return redirect('donaredapp:index')
    
    if request.method == 'POST':
        # Get form data
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        zona_id = request.POST.get('zona')
        categoria_id = request.POST.get('categoria')
        
        # Update item fields
        item.nombre = nombre
        item.descripcion = descripcion
        
        # Get and set related objects
        try:
            zona = Zona.objects.get(pk=zona_id)
            item.zona = zona
        except Zona.DoesNotExist:
            messages.error(request, "La zona seleccionada no existe.")
            return redirect('donaredapp:editar_item', item_id=item_id)
            
        try:
            categoria = Categoria.objects.get(pk=categoria_id)
            item.categoria = categoria
        except Categoria.DoesNotExist:
            messages.error(request, "La categoría seleccionada no existe.")
            return redirect('donaredapp:editar_item', item_id=item_id)
        
        # Handle image update
        mantener_imagen = request.POST.get('mantener_imagen')
        nueva_imagen = request.FILES.get('imagen')
        
        if nueva_imagen and not mantener_imagen:
            # Check file size
            if nueva_imagen.size > settings.MAX_IMAGE_SIZE_BYTES:
                messages.error(request, f"La imagen no debe exceder {settings.MAX_IMAGE_SIZE_MB} MB.")
                return redirect('donaredapp:editar_item', item_id=item_id)
            
            # If there was a previous image, delete it
            if item.imagen:
                # Save the old image path to delete after saving the new one
                old_image_path = item.imagen.path if item.imagen else None
                
                # Set the new image
                item.imagen = nueva_imagen
                
                # Delete the old image file if it exists
                if old_image_path and os.path.isfile(old_image_path):
                    os.remove(old_image_path)
            else:
                item.imagen = nueva_imagen
        elif not mantener_imagen and item.imagen:
            # User unchecked "mantener_imagen" and didn't upload a new image, so remove the current one
            old_image_path = item.imagen.path
            item.imagen = None
            
            # Delete the image file
            if os.path.isfile(old_image_path):
                os.remove(old_image_path)
        
        # Save the updated item
        item.save()
        
        messages.success(request, "¡Ítem actualizado con éxito!")
        return redirect('donaredapp:tarjeta', item_id=item.id)
    
    # If not POST, redirect to the edit page
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