from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from .models import Item


def index(request):
    items_recientes = Item.objects.order_by("-fecha_creacion")[:5]
    context = {"items_recientes": items_recientes}
    return render(request, "donaredapp/index.html", context)

def tarjeta(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, "donaredapp/tarjeta.html", {"item": item})

def contacto(request, item_id):
    return HttpResponse("Estos son los datos de contacto del donante del item %s." % item_id)

def pedir(request, item_id):
    return HttpResponse("Estás solicitando el item %s." % item_id)