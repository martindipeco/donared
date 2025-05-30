from django.urls import path
from .views import GeoMapView, GeoJSONView

app_name = 'geo'

urlpatterns = [
    path('mapa/', GeoMapView.as_view(), name='mapa'),
    path('api/items/', GeoJSONView.as_view(), name='geo_items'),
] 