from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.contrib import messages
from .models import Item, Zona, Categoria
from .services.item_service import crear_item

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

def publicar(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        zona_id = request.POST.get("zona")
        categoria_id = request.POST.get("categoria")

        # Validación básica
        if not (nombre and descripcion and zona_id and categoria_id):
            return HttpResponseBadRequest("Todos los campos son obligatorios.")
        
        try:
            zona = Zona.objects.get(pk=zona_id)
            categoria = Categoria.objects.get(pk=categoria_id)
        except (Zona.DoesNotExist, Categoria.DoesNotExist):
            return HttpResponseBadRequest("Zona o categoría inválida.")
        
        # Crear y guardar el nuevo item
        item = Item(
            nombre=nombre,
            descripcion=descripcion,
            zona=zona,
            categoria=categoria
        )
        item.save()
        messages.success(request, "¡Item publicado con éxito!")
        return redirect("donaredapp:tarjeta", item_id=item.id)
    
    #asumiendo que el método es GET
    else:
        zonas = Zona.objects.all()
        categorias = Categoria.objects.all()
        context = {
            "zonas": zonas,
            "categorias": categorias,
        }
        return render(request, "donaredapp/publicar.html", context)


def pedir(request, item_id):
    return HttpResponse("Estás solicitando el item %s." % item_id)