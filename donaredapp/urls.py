from django.urls import path

from . import views
from . import views_auth
from . import views_items
from . import views_solicitudes

app_name = "donaredapp"

urlpatterns = [
    # Principales
    path('', views.index, name='index'),
    path('<int:item_id>/', views.tarjeta, name='tarjeta'),
    path('categorias/', views.categorias, name='categorias'),

    # Item management views
    path('publicar/', views_items.publicar, name='publicar'),
    path('<int:item_id>/editar_item/', views_items.editar_item, name='editar_item'),
    path('<int:item_id>/actualizar_item/', views_items.actualizar_item, name='actualizar_item'),
    path('<int:item_id>/ocultar_item/', views_items.ocultar_item, name='ocultar_item'),
    
    # Solicitud views
    path('<int:item_id>/pedir/', views_solicitudes.pedir, name='pedir'),
    path('solicitudes/', views_solicitudes.solicitudes, name='solicitudes'),
    path('donaciones/', views_solicitudes.donaciones, name='donaciones'),
    path('<int:solicitud_id>/gestionar/', views_solicitudes.gestionar_solicitud, name='gestionar_solicitud'),

    # Authentication URLs
    path('registro/', views_auth.registro, name='registro'),
    path('login/', views_auth.login_user, name='login'),
    path('logout/', views_auth.logout_user, name='logout'),
    path('perfil/', views_auth.perfil, name='perfil'),
    path('perfil/editar/', views_auth.editar_perfil, name='editar_perfil'),
    path('recuperapass', views_auth.recuperapass, name='recuperapass'),

    # URLs de Perfil y Reseñas
    path('perfil-donante/<str:username>/', views.perfil_donante, name='perfil_donante'),
    path('solicitud/<int:solicitud_id>/crear-resena/', views.crear_resena, name='crear_resena'),
    path('resena/<int:resena_id>/editar/', views.editar_resena, name='editar_resena'),
    path('resena/<int:resena_id>/eliminar/', views.eliminar_resena, name='eliminar_resena'),
    path('resenas/<str:username>/', views.ver_resenas, name='ver_resenas'),
    path('resenas/', views.ver_todas_resenas, name='ver_todas_resenas'),
    path('admin/resenas/', views.admin_resenas, name='admin_resenas'),
    path('admin/resena/<int:resena_id>/aprobar/', views.aprobar_resena, name='aprobar_resena'),
    path('admin/resena/<int:resena_id>/rechazar/', views.rechazar_resena, name='rechazar_resena'),
    path('admin/resena/<int:resena_id>/editar/', views.editar_resena_admin, name='editar_resena_admin'),
]