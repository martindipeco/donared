from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.core.paginator import Paginator
from .models import Item, Categoria, Solicitud, Resena
from .forms import ResenaForm
from django.contrib.auth.models import User

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

    for item in items_to_show:
        if item.usuario:
            item.promedio_calificacion_donante = get_promedio_calificaciones(item.usuario)
            item.total_resenas_donante = Resena.objects.filter(solicitud__donante=item.usuario).count()
        else:
            item.promedio_calificacion_donante = 0
            item.total_resenas_donante = 0

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
        # Primero intentamos obtener el item sin importar si está activo o no
        item = Item.objects.get(pk=item_id)
        
        # Si el item está inactivo, verificamos si el usuario tiene una solicitud relacionada
        if not item.activo and request.user.is_authenticated:
            has_solicitud = Solicitud.objects.filter(
                item=item,
                beneficiario=request.user
            ).exists()
            
            # Si el usuario no tiene una solicitud relacionada, lanzamos 404
            if not has_solicitud and request.user != item.usuario:
                raise Http404("No se encontró el item con ID %s." % item_id)
        elif not item.activo:
            # Si el item está inactivo y el usuario no está autenticado, lanzamos 404
            raise Http404("No se encontró el item con ID %s." % item_id)
            
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

    promedio_calificacion_donante = get_promedio_calificaciones(item.usuario)
    total_resenas_donante = Resena.objects.filter(solicitud__donante=item.usuario).count()

    context = {
        'item': item,
        'solicitud_aceptada': solicitud_aceptada,
        'has_solicitud': has_solicitud,
        'promedio_calificacion_donante': promedio_calificacion_donante,
        'total_resenas_donante': total_resenas_donante,
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
        
        # Añadir calificación y total de reseñas para cada item en la categoría
        for item in items_categoria:
            if item.usuario:
                item.promedio_calificacion_donante = get_promedio_calificaciones(item.usuario)
                item.total_resenas_donante = Resena.objects.filter(solicitud__donante=item.usuario).count()
            else:
                item.promedio_calificacion_donante = 0
                item.total_resenas_donante = 0
        
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

@login_required
def crear_resena(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que el usuario es el beneficiario y la solicitud está aceptada
    if request.user != solicitud.beneficiario:
        messages.error(request, "No tienes permiso para crear una reseña para esta solicitud.")
        return redirect('donaredapp:solicitudes')
    
    if solicitud.estado != 'COMPLETADA':
        messages.error(request, "Solo puedes crear reseñas para solicitudes completadas.")
        return redirect('donaredapp:solicitudes')
    
    # Verificar si ya existe una reseña
    if hasattr(solicitud, 'resena'):
        messages.error(request, "Ya has creado una reseña para esta solicitud.")
        return redirect('donaredapp:solicitudes')
    
    if request.method == 'POST':
        form = ResenaForm(request.POST)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.solicitud = solicitud
            resena.save()
            messages.success(request, "¡Gracias por tu reseña!")
            return redirect('donaredapp:solicitudes')
    else:
        form = ResenaForm()
    
    return render(request, 'donaredapp/crear_resena.html', {
        'form': form,
        'solicitud': solicitud
    })

@login_required
def editar_resena(request, resena_id):
    resena = get_object_or_404(Resena, id=resena_id)
    
    # Verificar que el usuario es el autor de la reseña
    if request.user != resena.solicitud.beneficiario:
        messages.error(request, "No tienes permiso para editar esta reseña.")
        return redirect('donaredapp:solicitudes')
    
    if request.method == 'POST':
        form = ResenaForm(request.POST, instance=resena)
        if form.is_valid():
            form.save()
            messages.success(request, "Reseña actualizada correctamente.")
            return redirect('donaredapp:ver_resenas', username=resena.solicitud.donante.username)
    else:
        form = ResenaForm(instance=resena)
    
    return render(request, 'donaredapp/editar_resena.html', {
        'form': form,
        'resena': resena
    })

@login_required
def eliminar_resena(request, resena_id):
    resena = get_object_or_404(Resena, id=resena_id)
    
    # Verificar que el usuario es el autor de la reseña
    if request.user != resena.solicitud.beneficiario:
        messages.error(request, "No tienes permiso para eliminar esta reseña.")
        return redirect('donaredapp:solicitudes')
    
    if request.method == 'POST':
        resena.delete()
        messages.success(request, "Reseña eliminada correctamente.")
        return redirect('donaredapp:ver_resenas', username=resena.solicitud.donante.username)
    
    return render(request, 'donaredapp/eliminar_resena.html', {
        'resena': resena
    })

def ver_resenas(request, username):
    resenas = Resena.objects.filter(solicitud__donante__username=username)
    donante = resenas.first().solicitud.donante if resenas.exists() else None
    
    # Calcular estadísticas
    total_resenas = resenas.count()
    promedio_calificacion = resenas.aggregate(Avg('calificacion'))['calificacion__avg'] or 0
    
    # Paginación
    paginator = Paginator(resenas, 10)  # 10 reseñas por página
    page = request.GET.get('page')
    resenas = paginator.get_page(page)
    
    return render(request, 'donaredapp/ver_resenas.html', {
        'resenas': resenas,
        'donante': donante,
        'total_resenas': total_resenas,
        'promedio_calificacion': promedio_calificacion
    })

def ver_todas_resenas(request):
    resenas = Resena.objects.all()
    
    # Filtros
    search_query = request.GET.get('search', '')
    if search_query:
        resenas = resenas.filter(
            solicitud__donante__username__icontains=search_query
        ) | resenas.filter(
            solicitud__beneficiario__username__icontains=search_query
        ) | resenas.filter(
            comentario__icontains=search_query
        )
    
    # Ordenamiento
    sort = request.GET.get('sort', 'recent')
    if sort == 'rating':
        resenas = resenas.order_by('-calificacion')
    elif sort == 'oldest':
        resenas = resenas.order_by('fecha_creacion')
    else:  # recent
        resenas = resenas.order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(resenas, 12)  # 12 reseñas por página
    page = request.GET.get('page')
    resenas = paginator.get_page(page)
    
    return render(request, 'donaredapp/ver_todas_resenas.html', {
        'resenas': resenas,
        'search_query': search_query,
        'sort': sort
    })

@login_required
def admin_resenas(request):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('donaredapp:index')
    
    resenas = Resena.objects.all()
    
    # Filtros
    status = request.GET.get('status', 'all')
    if status != 'all':
        resenas = resenas.filter(estado=status)
    
    search_query = request.GET.get('search', '')
    if search_query:
        resenas = resenas.filter(
            solicitud__donante__username__icontains=search_query
        ) | resenas.filter(
            solicitud__beneficiario__username__icontains=search_query
        ) | resenas.filter(
            comentario__icontains=search_query
        )
    
    # Estadísticas
    total_resenas = Resena.objects.count()
    resenas_pendientes = Resena.objects.filter(estado='pending').count()
    resenas_aprobadas = Resena.objects.filter(estado='approved').count()
    resenas_rechazadas = Resena.objects.filter(estado='rejected').count()
    
    # Paginación
    paginator = Paginator(resenas, 20)  # 20 reseñas por página
    page = request.GET.get('page')
    resenas = paginator.get_page(page)
    
    return render(request, 'donaredapp/admin_resenas.html', {
        'resenas': resenas,
        'total_resenas': total_resenas,
        'resenas_pendientes': resenas_pendientes,
        'resenas_aprobadas': resenas_aprobadas,
        'resenas_rechazadas': resenas_rechazadas,
        'status': status,
        'search_query': search_query
    })

@login_required
def aprobar_resena(request, resena_id):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('donaredapp:index')
    
    resena = get_object_or_404(Resena, id=resena_id)
    resena.estado = 'approved'
    resena.save()
    messages.success(request, "Reseña aprobada correctamente.")
    return redirect('donaredapp:admin_resenas')

@login_required
def rechazar_resena(request, resena_id):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('donaredapp:index')
    
    resena = get_object_or_404(Resena, id=resena_id)
    resena.estado = 'rejected'
    resena.save()
    messages.success(request, "Reseña rechazada correctamente.")
    return redirect('donaredapp:admin_resenas')

@login_required
def editar_resena_admin(request, resena_id):
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('donaredapp:index')
    
    resena = get_object_or_404(Resena, id=resena_id)
    
    if request.method == 'POST':
        form = ResenaForm(request.POST, instance=resena)
        if form.is_valid():
            form.save()
            messages.success(request, "Reseña actualizada correctamente.")
            return redirect('donaredapp:admin_resenas')
    else:
        form = ResenaForm(instance=resena)
    
    return render(request, 'donaredapp/editar_resena_admin.html', {
        'form': form,
        'resena': resena
    })

def get_promedio_calificaciones(usuario):
    """Obtiene el promedio de calificaciones de un usuario"""
    resenas = Resena.objects.filter(solicitud__donante=usuario, estado='approved')
    promedio = resenas.aggregate(Avg('calificacion'))['calificacion__avg']
    return promedio if promedio is not None else 0

def perfil_donante(request, username):
    donante = get_object_or_404(User, username=username)
    resenas = Resena.objects.filter(solicitud__donante=donante, estado='approved').order_by('-fecha_creacion')[:3]
    
    total_resenas = Resena.objects.filter(solicitud__donante=donante, estado='approved').count()
    promedio_calificacion = get_promedio_calificaciones(donante)

    # Contar reseñas por calificación
    calificaciones_count = {}
    for i in range(1, 6):
        calificaciones_count[i] = Resena.objects.filter(solicitud__donante=donante, calificacion=i, estado='approved').count()
    
    porcentajes_calificaciones = {}
    if total_resenas > 0:
        for i in range(1, 6):
            porcentajes_calificaciones[str(i)] = (calificaciones_count.get(i, 0) / total_resenas) * 100
    
    context = {
        'donante': donante,
        'resenas': resenas,
        'total_resenas': total_resenas,
        'promedio_calificacion': promedio_calificacion,
        'calificaciones_count': calificaciones_count,
        'porcentajes_calificaciones': porcentajes_calificaciones,
    }
    return render(request, 'donaredapp/perfil_donante.html', context)