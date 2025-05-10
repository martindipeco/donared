# donaredapp/tests/test_views_solicitudes.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from donaredapp.models import Item, Zona, Categoria, Solicitud

class SolicitudTest(TestCase):
    def setUp(self):
        # Create test users
        self.donante = User.objects.create_user(
            username='donante',
            email='donante@example.com',
            password='testpassword123'
        )
        
        self.beneficiario = User.objects.create_user(
            username='beneficiario',
            email='beneficiario@example.com',
            password='testpassword123'
        )
        
        # Create test zona, categoria, and item
        self.zona = Zona.objects.create(nombre='CABA')
        self.categoria = Categoria.objects.create(nombre='Muebles')
        self.item = Item.objects.create(
            nombre='Mesa',
            descripcion='Una mesa',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.donante,
            activo=True
        )
        
        # Set up client
        self.client = Client()
    
    def test_pedir_authenticated(self):
        """Test that authenticated users can request an item"""
        # Log in as beneficiario
        self.client.login(username='beneficiario', password='testpassword123')
        
        # Make a request for the item
        response = self.client.get(
            reverse('donaredapp:pedir', kwargs={'item_id': self.item.id})
        )
        
        # Check redirect after successful request
        self.assertEqual(response.status_code, 200)  # or 302 if it redirects
        
        # Check that a solicitud was created
        self.assertTrue(
            Solicitud.objects.filter(
                item=self.item,
                beneficiario=self.beneficiario,
                donante=self.donante
            ).exists()
        )
    
    # Add more tests for solicitudes, donaciones, gestionar_solicitud...