# donaredapp/tests/test_views_items.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from donaredapp.models import Item, Zona, Categoria

class ItemCreationTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create test zona and categoria
        self.zona = Zona.objects.create(nombre='CABA')
        self.categoria = Categoria.objects.create(nombre='Muebles')
        
        # Set up client
        self.client = Client()
        
    def test_publicar_get(self):
        """Test that authenticated users can access the publicar form"""
        # Log in
        self.client.login(username='testuser', password='testpassword123')
        
        # Access the publicar page
        response = self.client.get(reverse('donaredapp:publicar'))
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check form elements are present
        self.assertContains(response, 'nombre')
        self.assertContains(response, 'zona')
        self.assertContains(response, 'categoria')

    def test_publicar_unauthenticated_redirects(self):
        """Test that unauthenticated users are redirected from publicar"""
        # Without logging in, try to access publicar
        response = self.client.get(reverse('donaredapp:publicar'))
        
        # Check for redirect
        self.assertEqual(response.status_code, 302)
        
    # Add more tests for editar_item, actualizar_item, ocultar_item...