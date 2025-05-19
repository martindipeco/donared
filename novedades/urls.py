from django.urls import path
from . import views

app_name = 'novedades'

urlpatterns = [
    path('', views.NoticiaListView.as_view(), name='noticia_list'),
    path('<int:pk>/', views.NoticiaDetailView.as_view(), name='noticia_detail'),
] 