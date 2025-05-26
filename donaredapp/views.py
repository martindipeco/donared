from django.shortcuts import render
from django.http import Http404
from django.contrib import messages
from .models import Item, Zona, Categoria, Solicitud

def index(request):
    # Get search parameters from GET request
    search_query = request.GET.get('q', '')
    zona_id = request.GET.get('zona', '')
    categoria_id = request.GET.get('categoria', '')
    page = int(request.GET.get('page', 1))  # Get current page, default to 1

    # Start with active items, ordered by creation date
    items = Item.objects.filter(activo=True).order_by("-fecha_creacion")

    # Apply filters if provided
    if search_query:
        items = items.filter(nombre__icontains=search_query)
    
    if zona_id:
        items = items.filter(zona_id=zona_id)
    
    if categoria_id:
        items = items.filter(categoria_id=categoria_id)


    # Calculate items to show based on page
    items_per_page = 4
    start_index = (page - 1) * items_per_page  
    end_index = start_index + items_per_page   

    # Get the items for current page
    items_to_show = items[start_index:end_index]
    
    # Check if there are more items to show
    hay_mas = items.count() > end_index

    # If no search parameters were provided, limit to 4 most recent items
    #if not any([search_query, zona_id, categoria_id]):
    #    items = items[:4]

    # Get all zones and categories for the dropdown menus
    zonas = Zona.objects.all()
    categorias = Categoria.objects.all()

    # Check for pending solicitudes if user is authenticated
    solicitudes_pendientes = False
    if request.user.is_authenticated:
        solicitudes_pendientes = Solicitud.objects.filter(
            donante=request.user, 
            estado="PENDIENTE"
        ).exists()

    context = {
        "items_recientes": items_to_show,
        "zonas": zonas,
        "categorias": categorias,
        "solicitudes_pendientes": solicitudes_pendientes,
        "hay_mas": hay_mas,
        "next_page": page + 1,
        "prev_page": page - 1 if page > 1 else None,  
        "current_search": {
            'q': search_query,
            'zona': zona_id,
            'categoria': categoria_id,
        }
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
    
    solicitud_aceptada = False
    has_solicitud = False
    if request.user.is_authenticated and request.user != item.usuario:
        # Check if the user has an accepted Solicitud for this item
        solicitud_aceptada = Solicitud.objects.filter(
            item=item,
            beneficiario=request.user,
            estado='ACEPTADA'
        ).exists()
        # Check if the user has any Solicitud for this item
        has_solicitud = Solicitud.objects.filter(
            item=item,
            beneficiario=request.user
        ).exists()

    context = {
        'item': item,
        'solicitud_aceptada': solicitud_aceptada,
        'has_solicitud': has_solicitud,
    }
    return render(request, "donaredapp/tarjeta.html", context)

def categorias(request):
    # Limpiar mensajes de la sesión
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # just iterating over them clears them

    categorias = Categoria.objects.all()
    context = {
        'categorias': categorias,
    }
    return render(request, "donaredapp/categorias.html", context)