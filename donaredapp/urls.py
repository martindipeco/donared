from django.urls import path

from . import views
from . import views_auth

app_name = "donaredapp"

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:item_id>/', views.tarjeta, name='tarjeta'),
    path('<int:item_id>/contacto/', views.contacto, name='contacto'),
    path('<int:item_id>/pedir/', views.pedir, name='pedir'),
    path('publicar/', views.publicar, name='publicar'),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('donaciones/', views.donaciones, name='donaciones'),
    path('solicitud/<int:solicitud_id>/gestionar/', views.gestionar_solicitud, name='gestionar_solicitud'),
    path('<int:item_id>/editar_item/', views.editar_item, name='editar_item'),
    path('<int:item_id>/actualizar_item/', views.actualizar_item, name='actualizar_item'),
    path('<int:item_id>/ocultar_item/', views.ocultar_item, name='ocultar_item'),

    # Authentication URLs
    path('registro/', views_auth.registro, name='registro'),
    path('login/', views_auth.login_user, name='login'),
    path('logout/', views_auth.logout_user, name='logout'),
    path('perfil/', views_auth.perfil, name='perfil'),
    path('recuperapass', views_auth.recuperapass, name='recuperapass'),
]