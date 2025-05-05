from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Item, Zona, Categoria, Solicitud
from .services.item_service import ItemService

def index(request):
    # Get search parameters from GET request
    search_query = request.GET.get('q', '')
    zona_id = request.GET.get('zona', '')
    categoria_id = request.GET.get('categoria', '')

    # Start with active items, ordered by creation date
    items = Item.objects.filter(activo=True).order_by("-fecha_creacion")

    # Apply filters if provided
    if search_query:
        items = items.filter(nombre__icontains=search_query)
    
    if zona_id:
        items = items.filter(zona_id=zona_id)
    
    if categoria_id:
        items = items.filter(categoria_id=categoria_id)

    # If no search parameters were provided, limit to 5 most recent items
    if not any([search_query, zona_id, categoria_id]):
        items = items[:5]

    # Get all zones and categories for the dropdown menus
    zonas = Zona.objects.all()
    categorias = Categoria.objects.all()

    context = {
        "items_recientes": items,
        "zonas": zonas,
        "categorias": categorias,
    }

    return render(request, "donaredapp/index.html", context)

def tarjeta(request, item_id):
    # Limpiar mensajes de la sesión
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # just iterating over them clears them

    try:
        item = Item.objects.get(pk=item_id, activo=True)
    except Item.DoesNotExist:
        raise Http404("No se encontró el item con ID %s." % item_id)
    return render(request, "donaredapp/tarjeta.html", {"item": item})

def contacto(request, item_id):
    return HttpResponse("Estos son los datos de contacto del donante del item %s." % item_id)

@login_required
def publicar(request):
    if request.method == "POST":
        # delegamos en service para la lógica de negocio
        item_service = ItemService()
        result = item_service.crear_item(request.POST, user=request.user)
        
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
def pedir(request, item_id):
    # Get the item or return 404 if not found
    item = get_object_or_404(Item, pk=item_id)
    
    # Get the user who posted the item
    donante = item.usuario
    
    if donante is None:
        messages.warning(request, "Este item no tiene un donante asociado.")
        return redirect('donaredapp:tarjeta', item_id=item_id)
    
    # Check if the user is not requesting their own item
    if item.usuario == request.user:
        messages.error(request, "No podés solicitar tu propio artículo")
        return redirect('donaredapp:tarjeta', item_id=item_id)
    
    # Check if the user already requested this item
    existing_request = Solicitud.objects.filter(item=item, beneficiario=request.user).exists()
    if existing_request:
        messages.info(request, "Ya has solicitado este artículo anteriormente")
        return redirect('donaredapp:tarjeta', item_id=item_id)
    
    # Create the request
    solicitud = Solicitud(
        item=item,
        donante=item.usuario,
        beneficiario=request.user
    )
    solicitud.save()
    
    messages.success(request, "Solicitud enviada correctamente. El donante ha sido notificado.")
    
    # Create a context with item and donante information
    context = {
        'item': item,
        'donante': donante,
        # You could add more contact info here if needed
    }
    
    return render(request, 'donaredapp/pedir.html', context)

@login_required
def solicitudes(request):
    # Get all requests made by the user
    solicitudes = Solicitud.objects.filter(beneficiario=request.user).order_by('-fecha_creacion')
    
    return render(request, 'donaredapp/solicitudes.html', {
        'solicitudes': solicitudes,
    })

@login_required
def donaciones(request):
    # Get items from this user
    items = Item.objects.filter(usuario=request.user, activo=True)
    
    # Get all requests for the user's items
    solicitudes = Solicitud.objects.filter(donante=request.user).order_by('-fecha_creacion')
    
    return render(request, 'donaredapp/donaciones.html', {
        'solicitudes': solicitudes,
        'items': items,
    })

@login_required
def gestionar_solicitud(request, solicitud_id):
    # Get the request
    solicitud = get_object_or_404(Solicitud, id=solicitud_id, donante=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'aceptar':
            solicitud.estado = 'ACEPTADA'
            solicitud.save()
            messages.success(request, f"Has aceptado la solicitud de {solicitud.beneficiario.username}")
        
        elif action == 'rechazar':
            solicitud.estado = 'RECHAZADA'
            solicitud.save()
            messages.success(request, f"Has rechazado la solicitud de {solicitud.beneficiario.username}")
        
        elif action == 'completar':
            solicitud.estado = 'COMPLETADA'
            solicitud.save()
            
            # Mark the item as inactive (it's been given away)
            solicitud.item.activo = False
            solicitud.item.save()
            
            # Reject any other pending requests for this item
            Solicitud.objects.filter(
                item=solicitud.item, 
                estado='PENDIENTE'
            ).exclude(id=solicitud.id).update(estado='RECHAZADA')
            
            messages.success(request, f"Has completado la donación de {solicitud.item.nombre}")
    
    return redirect('donaredapp:donaciones')