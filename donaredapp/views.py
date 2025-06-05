from django.shortcuts import render
from django.http import Http404
from django.contrib import messages
from .models import Item, Categoria, Solicitud

def index(request):
    # Get search parameters from GET request
    search_query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    page = int(request.GET.get('page', 1))  # Get current page, default to 1

    # Start with active items, ordered by creation date
    items = Item.objects.filter(activo=True).order_by("-fecha_creacion")

    # Apply filters if provided
    if search_query:
        items = items.filter(nombre__icontains=search_query)
    
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

    # Get all categories for the dropdown menu
    categorias = Categoria.objects.all()

    # Create a mapping for easy access in template
    categorias_dict = {cat.nombre.lower(): cat.id for cat in categorias}

    # Check for solicitudes realizadas if user is authenticated
    hay_solicitudes_realizadas = False
    if request.user.is_authenticated:
        hay_solicitudes_realizadas = Solicitud.objects.filter(
            beneficiario=request.user, 
            estado__in=["PENDIENTE", "ACEPTADA"]
        ).exists()

    # Check for pedidos recibidos if user is authenticated
    hay_pedidos_recibidos = False
    if request.user.is_authenticated:
        hay_pedidos_recibidos = Solicitud.objects.filter(
            donante=request.user, 
            estado="PENDIENTE"
        ).exists()

    context = {
        "items_recientes": items_to_show,
        "categorias": categorias,
        "categorias_dict": categorias_dict,
        "hay_solicitudes_realizadas": hay_solicitudes_realizadas,
        "hay_pedidos_recibidos": hay_pedidos_recibidos,
        "hay_mas": hay_mas,
        "next_page": page + 1,
        "prev_page": page - 1 if page > 1 else None,  
        "current_search": {
            'q': search_query,
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
    # Create a mapping for easy access in template
    categorias_dict = {cat.nombre.lower(): cat.id for cat in categorias}

    # Get items for each category (limit to recent items, e.g., 4 per category)
    items_por_categoria = 4
    categorias_con_items = []
    
    for categoria in categorias:
        items_categoria = Item.objects.filter(
            activo=True, 
            categoria=categoria
        ).order_by("-fecha_creacion")[:items_por_categoria]
        
        categorias_con_items.append({
            'categoria': categoria,
            'items': items_categoria,
            'total_items': Item.objects.filter(activo=True, categoria=categoria).count()
        })

    context = {
        'categorias': categorias,
        'categorias_dict': categorias_dict,
        'categorias_con_items': categorias_con_items,
    }
    return render(request, "donaredapp/categorias.html", context)