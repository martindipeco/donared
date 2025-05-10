from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from donaredapp.models import Item, Zona, Categoria

class ItemAccessTest(TestCase):
    def setUp(self):
        # Create test users
        self.user_donante = User.objects.create_user(
            username='donante',
            email='donante@example.com',
            password='testpassword123'
        )
        
        self.user_beneficiario = User.objects.create_user(
            username='beneficiario',
            email='beneficiario@example.com',
            password='testpassword123'
        )
        
        # Create test zona and categoria
        self.zona = Zona.objects.create(nombre='CABA')
        self.categoria = Categoria.objects.create(nombre='Muebles')
        
        # Create active item
        self.item_activo = Item.objects.create(
            nombre='Silla activa',
            descripcion='Una silla en buen estado',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.user_donante,
            activo=True
        )
        
        # Create inactive item
        self.item_inactivo = Item.objects.create(
            nombre='Silla inactiva',
            descripcion='Una silla ya donada',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.user_donante,
            activo=False
        )
        
        # Create a test client
        self.client = Client()

    def test_active_item_accessible(self):
        """Test that active items are accessible through their URL"""
        # Try to access the active item
        response = self.client.get(
            reverse('donaredapp:tarjeta', kwargs={'item_id': self.item_activo.id})
        )
        
        # Check that the response is successful (status code 200)
        self.assertEqual(response.status_code, 200)
        
        # Check that the item name appears in the response
        self.assertContains(response, self.item_activo.nombre)

    def test_inactive_item_not_accessible(self):
        """Test that inactive items are not accessible through their URL"""
        # Try to access the inactive item
        response = self.client.get(
            reverse('donaredapp:tarjeta', kwargs={'item_id': self.item_inactivo.id})
        )
        
        # Check that the response is a 404 (not found)
        self.assertEqual(response.status_code, 404)
        
        # Alternatively, if your view redirects instead of showing a 404,
        # you might want to check for a redirect:
        # self.assertEqual(response.status_code, 302)

    def test_index_shows_only_active_items(self):
        """Test that the index page only shows active items"""
        # Access the index page
        response = self.client.get(reverse('donaredapp:index'))
        
        # Check the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that the active item is in the context
        self.assertIn('items_recientes', response.context)
        items = response.context['items_recientes']
        
        # Check that the active item is in the list
        self.assertIn(self.item_activo, items)
        
        # Check that the inactive item is NOT in the list
        self.assertNotIn(self.item_inactivo, items)
        
        # Additionally, check the rendered HTML
        self.assertContains(response, self.item_activo.nombre)
        self.assertNotContains(response, self.item_inactivo.nombre)

    def test_authenticated_user_cannot_access_inactive_item(self):
        """Test that even authenticated users cannot access inactive items"""
        # Log in as a user
        self.client.login(username='beneficiario', password='testpassword123')
        
        # Try to access the inactive item
        response = self.client.get(
            reverse('donaredapp:tarjeta', kwargs={'item_id': self.item_inactivo.id})
        )
        
        # Check that the response is a 404 (not found)
        self.assertEqual(response.status_code, 404)
