from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from donaredapp.models import Item, Categoria

# Create your views here.

class GeoMapView(TemplateView):
    template_name = 'geo/mapa.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        return context

class GeoJSONView(TemplateView):
    def get(self, request, *args, **kwargs):
        categoria_id = request.GET.get('categoria')
        items = Item.objects.filter(activo=True)
        
        if categoria_id:
            items = items.filter(categoria_id=categoria_id)
        
        items = items.filter(latitude__isnull=False, longitude__isnull=False)
        
        features = []
        for item in items:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [float(item.longitude), float(item.latitude)]
                },
                'properties': {
                    'id': item.id,
                    'nombre': item.nombre,
                    'categoria': item.categoria.nombre,
                    'url_foto': item.imagen.url if item.imagen else None,
                    'url_detalle': f'/{item.id}/'
                }
            })
        
        return JsonResponse({
            'type': 'FeatureCollection',
            'features': features
        })
