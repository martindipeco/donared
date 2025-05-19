from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Noticia

# Create your views here.

class NoticiaListView(ListView):
    model = Noticia
    template_name = 'novedades/noticia_list.html'
    context_object_name = 'noticias'
    paginate_by = 6  # Mostrar 6 noticias por página

    def get_queryset(self):
        return Noticia.objects.filter(estado='publicado').order_by('-fecha_publicacion')

class NoticiaDetailView(DetailView):
    model = Noticia
    template_name = 'novedades/noticia_detail.html'
    context_object_name = 'noticia'

    def get_queryset(self):
        return Noticia.objects.filter(estado='publicado')
