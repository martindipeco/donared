from django.shortcuts import get_object_or_404
from django.conf import settings
from ..models import Item, Categoria
from ..forms import ItemForm  # Importar ItemForm

class ItemService:

    def crear_item(self, form_data, files=None, user=None):
        """
        Creates a new Item based on form data
        
        Args:
            form_data: POST data from the request
            files: FILES data from the request
            user: The user creating this item (optional)
            
        Returns:
            dict: Result containing success status, item object if successful, 
                  or error message if unsuccessful
        """
        form = ItemForm(form_data, files) # Usar ItemForm
        
        if form.is_valid():
            try:
                item = form.save(commit=False) # Guardar el formulario sin persistir aún
                item.usuario = user # Asignar el usuario

                # Handle the image upload - form.save handles file field now
                # Check image size constraint (already in form clean, but double check here if needed)
                # if item.imagen and item.imagen.size > settings.MAX_IMAGE_SIZE_BYTES:
                #     return {
                #         'success': False,
                #         'error': f"La imagen no debe exceder {settings.MAX_IMAGE_SIZE_MB} MB"
                #     }

                item.save() # Persistir el item con lat/lon del clean method del form

                return {
                    'success': True,
                    'item': item
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Error al guardar el item: {str(e)}"
                }
        else:
            # Si el formulario no es válido, devolver los errores del formulario
            # Puedes formatear los errores como una cadena para el mensaje
            errors = form.errors.as_text()
            return {
                'success': False,
                'error': f"Errores de validación: {errors}"
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