from django.test import TestCase, Client
from django.urls import reverse
from django.http import Http404
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from donaredapp.models import Item, Zona, Categoria, Solicitud

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
        
class TarjetaViewTest(TestCase):
    def setUp(self):
        # Create test users
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpassword123'
        )
        
        self.validated_user = User.objects.create_user(
            username='validated_user',
            email='validated@example.com',
            password='testpassword123'
        )
        
        self.unvalidated_user = User.objects.create_user(
            username='unvalidated_user',
            email='unvalidated@example.com',
            password='testpassword123'
        )
        
        # Create or update profiles for users
        # Assuming Profile is automatically created or there's a signal
        # Set validation status
        self.owner.profile.validado = True
        self.owner.profile.save()
        
        self.validated_user.profile.validado = True
        self.validated_user.profile.save()
        
        self.unvalidated_user.profile.validado = False
        self.unvalidated_user.profile.save()
        
        # Create test zona, categoria
        self.zona = Zona.objects.create(nombre='CABA')
        self.categoria = Categoria.objects.create(nombre='Muebles')
        
        # Create test item
        self.item = Item.objects.create(
            nombre='Mesa de cocina',
            descripcion='Una mesa de cocina usada en buen estado',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.owner,
            activo=True
        )
        
        # Create an inactive item for testing
        self.inactive_item = Item.objects.create(
            nombre='Silla inactiva',
            descripcion='Una silla que no está disponible',
            zona=self.zona, 
            categoria=self.categoria,
            usuario=self.owner,
            activo=False
        )
        
        # Set up client
        self.client = Client()
    
    def test_tarjeta_view_item_exists(self):
        """Test that the view works correctly when item exists"""
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': self.item.id}))
        
        # Check response status code
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct template is used
        self.assertTemplateUsed(response, 'donaredapp/tarjeta.html')
        
        # Check that item is in the context
        self.assertIn('item', response.context)
        self.assertEqual(response.context['item'], self.item)
        
        # Check that the item details are displayed
        self.assertContains(response, self.item.nombre)
        self.assertContains(response, self.item.descripcion)
        self.assertContains(response, self.item.zona)
    
    def test_tarjeta_view_item_not_exists(self):
        """Test the view with non-existent item ID"""
        non_existent_id = 999  # Assuming this ID doesn't exist
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': non_existent_id}))
        
        # Check response status code (should be 404)
        self.assertEqual(response.status_code, 404)
    
    def test_tarjeta_view_inactive_item(self):
        """Test the view with an inactive item"""
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': self.inactive_item.id}))
        
        # Check response status code (should be 404)
        self.assertEqual(response.status_code, 404)
    
    def test_tarjeta_view_anonymous_user(self):
        """Test the view for anonymous (not logged in) users"""
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': self.item.id}))
        
        # Check that registration link is shown
        self.assertContains(response, 'Registrate para poder contactar al donante')
        self.assertContains(response, reverse('donaredapp:registro'))
        
        # Check that owner buttons are not shown
        self.assertNotContains(response, 'Editar')
        self.assertNotContains(response, 'Dar de baja')
        
        # Check that contact button is not shown
        self.assertNotContains(response, 'Contactar donante')
        
        # Check that validation message is not shown
        self.assertNotContains(response, 'Necesitas validar tu cuenta')
    
    def test_tarjeta_view_item_owner(self):
        """Test the view for the item owner"""
        # Log in as the item owner
        self.client.login(username='owner', password='testpassword123')
        
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': self.item.id}))
        
        # Check that edit and deactivate buttons are shown
        self.assertContains(response, 'Editar')
        self.assertContains(response, reverse('donaredapp:editar_item', kwargs={'item_id': self.item.id}))
        self.assertContains(response, 'Dar de baja')
        self.assertContains(response, reverse('donaredapp:ocultar_item', kwargs={'item_id': self.item.id}))
        
        # Check that contact button is not shown
        self.assertNotContains(response, 'Contactar donante')
        
        # Check that registration link is not shown
        self.assertNotContains(response, 'Registrate para poder contactar')
        
        # Check that validation message is not shown
        self.assertNotContains(response, 'Necesitas validar tu cuenta')
    
    def test_tarjeta_view_validated_user(self):
        """Test the view for a validated user who is not the owner"""
        # Log in as validated user
        self.client.login(username='validated_user', password='testpassword123')
        
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': self.item.id}))
        
        # Check that contact button is shown
        self.assertContains(response, 'Contactar donante')
        self.assertContains(response, reverse('donaredapp:pedir', kwargs={'item_id': self.item.id}))
        
        # Check that owner buttons are not shown
        self.assertNotContains(response, 'Editar')
        self.assertNotContains(response, 'Dar de baja')
        
        # Check that registration link is not shown
        self.assertNotContains(response, 'Registrate para poder contactar')
        
        # Check that validation message is not shown
        self.assertNotContains(response, 'Necesitas validar tu cuenta')
    
    def test_tarjeta_view_unvalidated_user(self):
        """Test the view for an unvalidated user"""
        # Log in as unvalidated user
        self.client.login(username='unvalidated_user', password='testpassword123')
        
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': self.item.id}))
        
        # Check that validation message is shown
        self.assertContains(response, 'Necesitas validar tu cuenta para contactar al donante')
        
        # Check that contact button is not shown
        self.assertNotContains(response, 'Contactar donante')
        
        # Check that owner buttons are not shown
        self.assertNotContains(response, 'Editar')
        self.assertNotContains(response, 'Dar de baja')
        
        # Check that registration link is not shown
        self.assertNotContains(response, 'Registrate para poder contactar')
    
    def test_tarjeta_view_with_image(self):
        """Test that the view correctly displays an item with an image"""
        # Create a simple image file for testing
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  # Empty content for testing
            content_type='image/jpeg'
        )
        
        # Create an item with an image
        item_with_image = Item.objects.create(
            nombre='Mesa con imagen',
            descripcion='Una mesa con imagen',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.owner,
            activo=True,
            imagen=image_file
        )
        
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': item_with_image.id}))
        
        # Check that the image div is present
        self.assertContains(response, 'item-imagen')
        self.assertContains(response, f'src="{item_with_image.imagen.url}"')
    
    def test_tarjeta_view_clears_messages(self):
        """Test that the view clears messages from the session"""
        # Add a message to the session
        session = self.client.session
        session['_messages'] = ['Test message']
        session.save()
        
        # Access the view
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': self.item.id}))
        
        # Check that there are no messages in the response
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)
    
    def test_tarjeta_view_common_elements(self):
        """Test that common elements are present in all user scenarios"""
        # Test for anonymous user
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': self.item.id}))
        self.assertContains(response, 'Volver a inicio')
        self.assertContains(response, reverse('donaredapp:index'))
        
        # Test for item owner
        self.client.login(username='owner', password='testpassword123')
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': self.item.id}))
        self.assertContains(response, 'Volver a inicio')
        self.assertContains(response, reverse('donaredapp:index'))
        
        # Test for validated user
        self.client.login(username='validated_user', password='testpassword123')
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': self.item.id}))
        self.assertContains(response, 'Volver a inicio')
        self.assertContains(response, reverse('donaredapp:index'))
        
        # Test for unvalidated user
        self.client.login(username='unvalidated_user', password='testpassword123')
        response = self.client.get(reverse('donaredapp:tarjeta', kwargs={'item_id': self.item.id}))
        self.assertContains(response, 'Volver a inicio')
        self.assertContains(response, reverse('donaredapp:index'))

class TarjetaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test data
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        self.zona = Zona.objects.create(nombre='Test Zona')
        self.categoria = Categoria.objects.create(nombre='Test Categoria')
        self.item = Item.objects.create(
            nombre='Test Item',
            descripcion='Test Description',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.user1,
            domicilio='123 Test St',
            activo=True
        )

        # Create a profile for user2 (assuming Profile model exists)
        self.user2.profile.validado = True
        self.user2.profile.save()

    def test_solicitud_aceptada_owner(self):
        # Test when user is the item owner
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('donaredapp:tarjeta', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['solicitud_aceptada'])

    def test_solicitud_aceptada_accepted(self):
        # Test when user has an accepted Solicitud
        Solicitud.objects.create(
            item=self.item,
            donante=self.user1,
            beneficiario=self.user2,
            estado='ACEPTADA'
        )
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('donaredapp:tarjeta', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['solicitud_aceptada'])

    def test_solicitud_aceptada_pending(self):
        # Test when user has a pending Solicitud
        Solicitud.objects.create(
            item=self.item,
            donante=self.user1,
            beneficiario=self.user2,
            estado='PENDIENTE'
        )
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('donaredapp:tarjeta', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['solicitud_aceptada'])

    def test_solicitud_aceptada_rejected(self):
        # Test when user has a rejected Solicitud
        Solicitud.objects.create(
            item=self.item,
            donante=self.user1,
            beneficiario=self.user2,
            estado='RECHAZADA'
        )
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('donaredapp:tarjeta', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['solicitud_aceptada'])

    def test_solicitud_aceptada_concretada(self):
        # Test when user has a concretada Solicitud
        Solicitud.objects.create(
            item=self.item,
            donante=self.user1,
            beneficiario=self.user2,
            estado='CONCRETADA'
        )
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('donaredapp:tarjeta', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['solicitud_aceptada'])

    def test_solicitud_aceptada_no_solicitud(self):
        # Test when user has no Solicitud
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('donaredapp:tarjeta', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['solicitud_aceptada'])

    def test_solicitud_aceptada_anonymous(self):
        # Test when user is not authenticated
        response = self.client.get(reverse('donaredapp:tarjeta', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['solicitud_aceptada'])

    def test_non_existent_item(self):
        # Test when item does not exist or is not active
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('donaredapp:tarjeta', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_has_solicitud_with_solicitud(self):
        # Test when user has a Solicitud (any status)
        Solicitud.objects.create(
            item=self.item,
            donante=self.user1,
            beneficiario=self.user2,
            estado='PENDIENTE'
        )
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('donaredapp:tarjeta', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_solicitud'])

    def test_has_solicitud_no_solicitud(self):
        # Test when user has no Solicitud
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('donaredapp:tarjeta', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_solicitud'])

    def test_has_solicitud_owner(self):
        # Test when user is the item owner
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('donaredapp:tarjeta', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_solicitud'])

    def test_has_solicitud_anonymous(self):
        # Test when user is not authenticated
        response = self.client.get(reverse('donaredapp:tarjeta', args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_solicitud'])