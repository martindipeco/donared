# donaredapp/tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from donaredapp.models import Item, Zona, Categoria, Solicitud

class ItemModelTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create test zona and categoria
        self.zona = Zona.objects.create(nombre='CABA')
        self.categoria = Categoria.objects.create(nombre='Muebles')
    
    def test_item_creation(self):
        """Test item can be created with basic fields"""
        item = Item.objects.create(
            nombre='Silla de prueba',
            descripcion='Una silla para testing',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.user
        )
        
        self.assertEqual(item.nombre, 'Silla de prueba')
        self.assertEqual(item.zona, self.zona)
        self.assertEqual(item.categoria, self.categoria)
        self.assertEqual(item.usuario, self.user)
        self.assertTrue(item.activo)  # Default value