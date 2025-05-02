from django.urls import path

from . import views

app_name = "donaredapp"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:item_id>/", views.tarjeta, name="tarjeta"),
    path("<int:item_id>/contacto/", views.contacto, name="contacto"),
    path("<int:item_id>/pedir/", views.pedir, name="pedir"),
    path("publicar/", views.publicar, name="publicar"),
]