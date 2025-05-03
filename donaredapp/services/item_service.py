from django.shortcuts import get_object_or_404
from ..models import Item, Zona, Categoria

class ItemService:

    def crear_item(self, form_data):
        # Extraer data del form
        nombre = form_data.get("nombre")
        descripcion = form_data.get("descripcion")
        zona_id = form_data.get("zona")
        categoria_id = form_data.get("categoria")

        # Validar campos obligatorios
        if not (nombre and descripcion and zona_id and categoria_id):
            return {
                'success': False,
                'error': "Todos los campos son obligatorios."
            }
        
        # Validar y obtener zona y categoría
        try:
            zona = Zona.objects.get(pk=zona_id)
            categoria = Categoria.objects.get(pk=categoria_id)
        except (Zona.DoesNotExist, Categoria.DoesNotExist):
            return {
                'success': False,
                'error': "Zona o categoría inválida."
            }
        
        # Crear y persistir el item
        try:
            item = Item(
                nombre=nombre,
                descripcion=descripcion,
                zona=zona,
                categoria=categoria
            )
            item.save()
            
            return {
                'success': True,
                'item': item
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error al crear el item: {str(e)}"
            }
        
    def get_items_recientes(self, limit=5):
        return Item.objects.order_by("-fecha_creacion")[:limit]