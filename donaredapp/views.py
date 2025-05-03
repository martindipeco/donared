from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Item, Zona, Categoria
from .services.item_service import ItemService

def index(request):
    items_recientes = Item.objects.order_by("-fecha_creacion")[:5]
    context = {"items_recientes": items_recientes}
    return render(request, "donaredapp/index.html", context)

def tarjeta(request, item_id):
    #item = get_object_or_404(Item, pk=item_id)
    try:
        item = Item.objects.get(pk=item_id)
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
    return HttpResponse("Estás solicitando el item %s." % item_id)