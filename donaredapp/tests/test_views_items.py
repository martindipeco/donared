# donaredapp/tests/test_views_items.py
import os
from unittest.mock import patch
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
        
class ItemUpdateTest(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword123'
        )
        
        # Create test zonas and categorias
        self.zona = Zona.objects.create(nombre='CABA')
        self.otra_zona = Zona.objects.create(nombre='Buenos Aires')
        self.categoria = Categoria.objects.create(nombre='Muebles')
        self.otra_categoria = Categoria.objects.create(nombre='Electrodomésticos')
        
        # Create a test item
        self.item = Item.objects.create(
            usuario=self.user,
            nombre='Test Item Original',
            descripcion='Description Original',
            zona=self.zona,
            categoria=self.categoria
        )
        
        # Set up client
        self.client = Client()
        
        # Create a test image for uploads
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  # Empty content for testing
            content_type='image/jpeg'
        )

    def test_actualizar_item_successful(self):
        """Test successful item update with new data"""
        # Log in as the item owner
        self.client.login(username='testuser', password='testpassword123')
        
        # Prepare updated data
        updated_data = {
            'nombre': 'Test Item Updated',
            'descripcion': 'Description Updated',
            'zona': self.otra_zona.id,
            'categoria': self.otra_categoria.id,
            'mantener_imagen': 'on'  # Keep any existing image
        }
        
        # Submit the update form
        response = self.client.post(
            reverse('donaredapp:actualizar_item', args=[self.item.id]), 
            updated_data
        )
        
        # Check redirect to item card page
        self.assertRedirects(response, reverse('donaredapp:tarjeta', args=[self.item.id]))
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item was updated correctly
        self.assertEqual(self.item.nombre, 'Test Item Updated')
        self.assertEqual(self.item.descripcion, 'Description Updated')
        self.assertEqual(self.item.zona, self.otra_zona)
        self.assertEqual(self.item.categoria, self.otra_categoria)
        
        # Check for success message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("¡Ítem actualizado con éxito!" in message.message for message in messages))

    def test_actualizar_item_unauthorized(self):
        """Test that a user cannot update another user's item"""
        # Log in as a different user (not the item owner)
        self.client.login(username='otheruser', password='otherpassword123')
        
        # Try to update the item
        updated_data = {
            'nombre': 'Unauthorized Update',
            'descripcion': 'Should Not Work',
            'zona': self.zona.id,
            'categoria': self.categoria.id
        }
        
        response = self.client.post(
            reverse('donaredapp:actualizar_item', args=[self.item.id]), 
            updated_data
        )
        
        # Check redirect to index page
        self.assertRedirects(response, reverse('donaredapp:index'))
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item was NOT updated
        self.assertEqual(self.item.nombre, 'Test Item Original')
        self.assertEqual(self.item.descripcion, 'Description Original')
        
        # Check for error message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("No tienes permiso para editar este ítem" in message.message for message in messages))

    def test_actualizar_item_unauthenticated(self):
        """Test that an unauthenticated user cannot update an item"""
        # No login
        
        # Try to update the item
        updated_data = {
            'nombre': 'Unauthenticated Update',
            'descripcion': 'Should Not Work',
            'zona': self.zona.id,
            'categoria': self.categoria.id
        }
        
        # Get the URL for updating the item
        update_url = reverse('donaredapp:actualizar_item', args=[self.item.id])
        
        # Make the POST request
        response = self.client.post(update_url, updated_data)
        
        # Check that the response is a redirect to login
        self.assertEqual(response.status_code, 302)
        
        # Check redirect URL contains login path
        redirect_url = response.url
        self.assertTrue(
            redirect_url.startswith('/login/') or 
            redirect_url.startswith('/accounts/login/')
        )
        
        # Verify the next parameter contains the original URL
        self.assertIn(update_url, redirect_url)
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item was NOT updated
        self.assertEqual(self.item.nombre, 'Test Item Original')
        self.assertEqual(self.item.descripcion, 'Description Original')

    def test_actualizar_item_invalid_zona(self):
        """Test update with invalid zone ID"""
        # Log in as the item owner
        self.client.login(username='testuser', password='testpassword123')
        
        # Prepare updated data with invalid zona
        updated_data = {
            'nombre': 'Invalid Zone Update',
            'descripcion': 'Should Not Update',
            'zona': 9999,  # Non-existent zona ID
            'categoria': self.categoria.id,
            'mantener_imagen': 'on'
        }
        
        # Submit the update form
        response = self.client.post(
            reverse('donaredapp:actualizar_item', args=[self.item.id]), 
            updated_data
        )
        
        # Check redirect to edit item page
        self.assertRedirects(response, reverse('donaredapp:editar_item', args=[self.item.id]))
        
        # Check for error message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("La zona seleccionada no existe" in message.message for message in messages))
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item was NOT updated
        self.assertEqual(self.item.nombre, 'Test Item Original')

    def test_actualizar_item_invalid_categoria(self):
        """Test update with invalid category ID"""
        # Log in as the item owner
        self.client.login(username='testuser', password='testpassword123')
        
        # Prepare updated data with invalid categoria
        updated_data = {
            'nombre': 'Invalid Category Update',
            'descripcion': 'Should Not Update',
            'zona': self.zona.id,
            'categoria': 9999,  # Non-existent categoria ID
            'mantener_imagen': 'on'
        }
        
        # Submit the update form
        response = self.client.post(
            reverse('donaredapp:actualizar_item', args=[self.item.id]), 
            updated_data
        )
        
        # Check redirect to edit item page
        self.assertRedirects(response, reverse('donaredapp:editar_item', args=[self.item.id]))
        
        # Check for error message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("La categoría seleccionada no existe" in message.message for message in messages))
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item was NOT updated
        self.assertEqual(self.item.nombre, 'Test Item Original')

    def test_actualizar_item_upload_new_image(self):
        """Test updating an item with a new image upload"""
        # Log in as the item owner
        self.client.login(username='testuser', password='testpassword123')
        
        # Prepare updated data with new image
        updated_data = {
            'nombre': 'Image Update Test',
            'descripcion': 'Testing image update',
            'zona': self.zona.id,
            'categoria': self.categoria.id,
            'imagen': self.test_image
        }
        
        # Submit the update form
        response = self.client.post(
            reverse('donaredapp:actualizar_item', args=[self.item.id]), 
            updated_data
        )
        
        # Check redirect to item card page
        self.assertRedirects(response, reverse('donaredapp:tarjeta', args=[self.item.id]))
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item was updated correctly
        self.assertEqual(self.item.nombre, 'Image Update Test')
        self.assertTrue(self.item.imagen)  # Verify image exists
        
        # Check for success message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("¡Ítem actualizado con éxito!" in message.message for message in messages))

    def test_actualizar_item_remove_image(self):
        """Test removing an item's image"""
        # First, add an image to the item
        self.item.imagen = self.test_image
        self.item.save()
        
        # Log in as the item owner
        self.client.login(username='testuser', password='testpassword123')
        
        # Prepare updated data without maintaining image
        updated_data = {
            'nombre': 'Remove Image Test',
            'descripcion': 'Testing image removal',
            'zona': self.zona.id,
            'categoria': self.categoria.id,
            # mantener_imagen is NOT included - should remove the image
        }
        
        # Mock the os.path.isfile and os.remove to prevent actual file operations
        with patch('os.path.isfile', return_value=True), patch('os.remove'):
            # Submit the update form
            response = self.client.post(
                reverse('donaredapp:actualizar_item', args=[self.item.id]), 
                updated_data
            )
        
        # Check redirect to item card page
        self.assertRedirects(response, reverse('donaredapp:tarjeta', args=[self.item.id]))
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item was updated correctly and image was removed
        self.assertEqual(self.item.nombre, 'Remove Image Test')
        self.assertFalse(self.item.imagen)  # Verify image is None/empty
        
        # Check for success message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("¡Ítem actualizado con éxito!" in message.message for message in messages))

    def test_actualizar_item_get_request(self):
        """Test that GET requests are redirected to edit page"""
        # Log in as the item owner
        self.client.login(username='testuser', password='testpassword123')
        
        # Make a GET request to actualizar_item
        response = self.client.get(reverse('donaredapp:actualizar_item', args=[self.item.id]))
        
        # Check redirect to edit item page
        self.assertRedirects(response, reverse('donaredapp:editar_item', args=[self.item.id]))
            
class ItemOcultarTest(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword123'
        )
        
        # Create test zonas and categorias
        self.zona = Zona.objects.create(nombre='CABA')
        self.categoria = Categoria.objects.create(nombre='Muebles')
        
        # Create a test item
        self.item = Item.objects.create(
            usuario=self.user,
            nombre='Test Item',
            descripcion='Test Description',
            zona=self.zona,
            categoria=self.categoria,
            activo=True  # Ensure the item starts as active
        )
        
        # Set up client
        self.client = Client()

    def test_ocultar_item_successful(self):
        """Test successfully hiding an item by its owner"""
        # Log in as the item owner
        self.client.login(username='testuser', password='testpassword123')
        
        # Submit the hide item request
        response = self.client.post(
            reverse('donaredapp:ocultar_item', args=[self.item.id])
        )
        
        # Check redirect to index page
        self.assertRedirects(response, reverse('donaredapp:index'))
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item was hidden correctly
        self.assertFalse(self.item.activo)
        
        # Check for success message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("¡Item ocultado con éxito!" in message.message for message in messages))

    def test_ocultar_item_unauthorized(self):
        """Test that a user cannot hide another user's item"""
        # Log in as a different user (not the item owner)
        self.client.login(username='otheruser', password='otherpassword123')
        
        # Try to hide the item
        response = self.client.post(
            reverse('donaredapp:ocultar_item', args=[self.item.id])
        )
        
        # Check that a 404 is returned
        self.assertEqual(response.status_code, 404)
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item was NOT hidden
        self.assertTrue(self.item.activo)

    def test_ocultar_item_unauthenticated(self):
        """Test that an unauthenticated user cannot hide an item"""
        # No login
        
        # Try to hide the item
        hide_url = reverse('donaredapp:ocultar_item', args=[self.item.id])
        response = self.client.post(hide_url)
        
        # Check that the response is a redirect to login
        self.assertEqual(response.status_code, 302)
        
        # Check redirect URL contains login path
        redirect_url = response.url
        self.assertTrue(
            redirect_url.startswith('/login/') or 
            redirect_url.startswith('/accounts/login/')
        )
        
        # Verify the next parameter contains the original URL
        self.assertIn(hide_url, redirect_url)
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item was NOT hidden
        self.assertTrue(self.item.activo)

    def test_ocultar_item_nonexistent(self):
        """Test hiding a non-existent item"""
        # Log in as a user
        self.client.login(username='testuser', password='testpassword123')
        
        # Try to hide a non-existent item with ID 9999
        non_existent_id = 9999
        response = self.client.post(
            reverse('donaredapp:ocultar_item', args=[non_existent_id])
        )
        
        # Should return a 404 response
        self.assertEqual(response.status_code, 404)

    def test_ocultar_item_already_hidden(self):
        """Test hiding an already hidden item"""
        # First, hide the item
        self.item.activo = False
        self.item.save()
        
        # Log in as the item owner
        self.client.login(username='testuser', password='testpassword123')
        
        # Try to hide the already hidden item
        response = self.client.post(
            reverse('donaredapp:ocultar_item', args=[self.item.id])
        )
        
        # Check redirect to index page
        self.assertRedirects(response, reverse('donaredapp:index'))
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item is still hidden
        self.assertFalse(self.item.activo)
        
        # Check for success message (should still show success)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("¡Item ocultado con éxito!" in message.message for message in messages))

    def test_ocultar_item_get_request(self):
        """Test that GET requests are not allowed (should be POST only)"""
        # Log in as the item owner
        self.client.login(username='testuser', password='testpassword123')
        
        # Make a GET request to ocultar_item
        response = self.client.get(reverse('donaredapp:ocultar_item', args=[self.item.id]))
        
        self.assertRedirects(response, reverse('donaredapp:index'))
        
        # Refresh the item from the database
        self.item.refresh_from_db()
        
        # Verify item was hidden
        self.assertFalse(self.item.activo)