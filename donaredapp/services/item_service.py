from django.shortcuts import get_object_or_404
from ..models import Item, Zona, Categoria

class ItemService:

    def crear_item(self, form_data, files=None, user=None):
        """
        Creates a new Item based on form data
        
        Args:
            form_data: POST data from the request
            user: The user creating this item (optional)
            
        Returns:
            dict: Result containing success status, item object if successful, 
                  or error message if unsuccessful
        """
        # Extraer data del form
        nombre = form_data.get("nombre")
        descripcion = form_data.get("descripcion")
        zona_id = form_data.get("zona")
        categoria_id = form_data.get("categoria")
        # Handle the image upload - get it from files parameter, not request.FILES
        imagen = None
        if files:
            imagen = files.get('imagen')


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
                categoria=categoria,
                usuario=user  # Associate with the user if provided
            )

            # Add image if provided
            if imagen:
                item.imagen = imagen

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
    
    def get_items_usuario(self, user):
        """
        Get items created by a specific user
        
        Args:
            user: User object
            
        Returns:
            QuerySet: Items created by the user
        """
        return Item.objects.filter(usuario=user).order_by("-fecha_creacion")
    
    
    def _requires_authentication(self):
        """
        Determines if authentication is required to create an item
        
        Returns:
            bool: True if authentication is required, False otherwise
        """
        # You can add logic here to make this configurable
        return True  # For now, always require authentication