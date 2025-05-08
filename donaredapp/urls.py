from django.urls import path

from . import views
from . import auth_views

app_name = "donaredapp"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:item_id>/", views.tarjeta, name="tarjeta"),
    path("<int:item_id>/contacto/", views.contacto, name="contacto"),
    path("<int:item_id>/pedir/", views.pedir, name="pedir"),
    path("publicar/", views.publicar, name="publicar"),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('donaciones/', views.donaciones, name='donaciones'),
    path('solicitud/<int:solicitud_id>/gestionar/', views.gestionar_solicitud, name='gestionar_solicitud'),

    # Authentication URLs
    path('registro/', auth_views.registro, name='registro'),
    path('login/', auth_views.login_user, name='login'),
    path('logout/', auth_views.logout_user, name='logout'),
    path('perfil/', auth_views.perfil, name='perfil'),
    path('recuperapass', auth_views.recuperapass, name='recuperapass'),
]