from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Item, Solicitud

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
    
    # Simplify domicile for display
    for solicitud in solicitudes:
        if solicitud.item and solicitud.item.domicilio:
            domicilio_parts = solicitud.item.domicilio.split(',')
            # Take up to the first three parts (street, number, locality)
            solicitud.display_domicilio = ', '.join(part.strip() for part in domicilio_parts[:3])
        else:
            solicitud.display_domicilio = "No especificado"
    
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
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que el usuario es el beneficiario o el donante
    if request.user != solicitud.beneficiario and request.user != solicitud.donante:
        messages.error(request, "No tienes permiso para gestionar esta solicitud")
        return redirect('donaredapp:index')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'aceptar' and request.user == solicitud.donante:
            solicitud.estado = 'ACEPTADA'
            solicitud.save()
            messages.success(request, f"Has aceptado la solicitud de {solicitud.beneficiario.username}")
        
        elif action == 'rechazar' and request.user == solicitud.donante:
            solicitud.estado = 'RECHAZADA'
            solicitud.save()
            messages.success(request, f"Has rechazado la solicitud de {solicitud.beneficiario.username}")
        
        elif action == 'completar' and request.user == solicitud.donante:
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
            
        elif action == 'baja' and request.user == solicitud.beneficiario:
            solicitud.delete()
            messages.success(request, "Has dado de baja la solicitud correctamente")
            return redirect('donaredapp:solicitudes')
    
    # Redirigir según el usuario
    if request.user == solicitud.donante:
        return redirect('donaredapp:donaciones')
    else:
        return redirect('donaredapp:solicitudes')