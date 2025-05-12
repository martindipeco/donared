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

    # PUBLICAR   
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

    # EDITAR
    def test_editar_item_get(self):
        """Test that an authenticated user can access the edit item page for their own item"""
        # Create an item for the test user
        item = Item.objects.create(
            usuario=self.user,
            nombre='Test Item',
            descripcion='Test Description',
            zona=self.zona,
            categoria=self.categoria
        )

        # Log in the test user
        self.client.login(username='testuser', password='testpassword123')

        # Access the edit item page
        response = self.client.get(reverse('donaredapp:editar_item', args=[item.id]))

        # Check response is successful
        self.assertEqual(response.status_code, 200)

        # Check context contains correct item
        self.assertEqual(response.context['item'], item)

        # Check editing flag is True
        self.assertTrue(response.context['editing'])

        # Verify zonas and categorias are in context
        self.assertIn('zonas', response.context)
        self.assertIn('categorias', response.context)

    def test_editar_item_unauthorized(self):
        """Test that a user cannot edit another user's item"""
        # Create an item belonging to another user
        another_user = User.objects.create_user(
            username='otheruser', 
            email='other@example.com', 
            password='otherpassword123'
        )
        item = Item.objects.create(
            usuario=another_user,
            nombre='Other User Item',
            descripcion='Other Description',
            zona=self.zona,
            categoria=self.categoria
        )

        # Log in the test user
        self.client.login(username='testuser', password='testpassword123')

        # Try to access the edit page for another user's item
        response = self.client.get(reverse('donaredapp:editar_item', args=[item.id]))

        # Check user is redirected
        self.assertRedirects(response, reverse('donaredapp:index'))

        # Check error message is in session
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("No tienes permiso para editar este ítem" in message.message for message in messages))

    def test_editar_item_unauthenticated(self):
        """Test that an unauthenticated user cannot access the edit item page"""
        # Create an item
        item = Item.objects.create(
            usuario=self.user,
            nombre='Test Item',
            descripcion='Test Description',
            zona=self.zona,
            categoria=self.categoria
        )

        # Try to access the edit page without logging in
        edit_item_url = reverse('donaredapp:editar_item', args=[item.id])
        response = self.client.get(edit_item_url)

        # Check that the response is a redirect
        self.assertEqual(response.status_code, 302, 
            f"Expected a redirect, but got status code {response.status_code}")

        # Print out the redirect URL for debugging
        redirect_url = response.url
        print(f"Redirect URL: {redirect_url}")

        # Check that the redirect URL contains the login path
        self.assertTrue(
            redirect_url.startswith('/login/') or 
            redirect_url.startswith('/accounts/login/'),
            f"Unexpected redirect URL: {redirect_url}"
        )

        # Check that the next parameter is in the redirect URL
        self.assertIn('next=', redirect_url, 
            "Redirect URL should contain 'next' parameter")
        
        # Verify the next parameter contains the original URL
        self.assertIn(edit_item_url, redirect_url, 
            "Next parameter should contain the original edit item URL")
            
    # Add more tests for actualizar_item, ocultar_item...