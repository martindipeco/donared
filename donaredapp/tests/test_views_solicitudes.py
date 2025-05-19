# donaredapp/tests/test_views_solicitudes.py
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.messages import get_messages
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

class SolicitudesViewTest(TestCase):
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
        
        # Create test zona, categoria, and items
        self.zona = Zona.objects.create(nombre='CABA')
        self.categoria = Categoria.objects.create(nombre='Muebles')
        
        self.item1 = Item.objects.create(
            nombre='Mesa',
            descripcion='Una mesa',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.donante,
            activo=True
        )
        
        self.item2 = Item.objects.create(
            nombre='Silla',
            descripcion='Una silla',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.donante,
            activo=True
        )
        
        # Create solicitudes with different dates to test ordering
        # Older solicitud
        self.solicitud1 = Solicitud.objects.create(
            item=self.item1,
            beneficiario=self.beneficiario,
            donante=self.donante,
            fecha_creacion=timezone.now() - timezone.timedelta(days=2)
        )
        
        # Newer solicitud
        self.solicitud2 = Solicitud.objects.create(
            item=self.item2,
            beneficiario=self.beneficiario,
            donante=self.donante,
            fecha_creacion=timezone.now() - timezone.timedelta(days=1)
        )
        
        # Set up client
        self.client = Client()
    
    def test_solicitudes_view_authenticated(self):
        """Test that authenticated users can access their solicitudes"""
        # Log in as beneficiario
        self.client.login(username='beneficiario', password='testpassword123')
        
        # Get the solicitudes page
        response = self.client.get(reverse('donaredapp:solicitudes'))
        
        # Check response status code
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct template is used
        self.assertTemplateUsed(response, 'donaredapp/solicitudes.html')
        
        # Check that the solicitudes are in the context
        self.assertIn('solicitudes', response.context)
        
        # Check that both solicitudes are returned
        self.assertEqual(len(response.context['solicitudes']), 2)
        
        # Check that the solicitudes are ordered by fecha_creacion in descending order
        # (newest first)
        self.assertEqual(response.context['solicitudes'][0], self.solicitud2)
        self.assertEqual(response.context['solicitudes'][1], self.solicitud1)
    
    def test_solicitudes_view_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        # Access the solicitudes page without being logged in
        response = self.client.get(reverse('donaredapp:solicitudes'))
        
        # Check that user is redirected to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
    
    def test_solicitudes_view_different_user(self):
        """Test that a user only sees their own solicitudes"""
        # Create another user
        other_user = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='testpassword123'
        )
        
        # Create a solicitud for the other user
        other_solicitud = Solicitud.objects.create(
            item=self.item1,
            beneficiario=other_user,
            donante=self.donante,
            fecha_creacion=timezone.now()
        )
        
        # Log in as beneficiario
        self.client.login(username='beneficiario', password='testpassword123')
        
        # Get the solicitudes page
        response = self.client.get(reverse('donaredapp:solicitudes'))
        
        # Check that only the beneficiario's solicitudes are returned
        solicitudes = response.context['solicitudes']
        self.assertEqual(len(solicitudes), 2)
        
        # Check that the other user's solicitud is not included
        self.assertNotIn(other_solicitud, solicitudes)
        
        # Log in as the other user
        self.client.logout()
        self.client.login(username='other_user', password='testpassword123')
        
        # Get the solicitudes page
        response = self.client.get(reverse('donaredapp:solicitudes'))
        
        # Check that only the other user's solicitude is returned
        solicitudes = response.context['solicitudes']
        self.assertEqual(len(solicitudes), 1)
        self.assertEqual(solicitudes[0], other_solicitud)
    
    def test_empty_solicitudes(self):
        """Test behavior when a user has no solicitudes"""
        # Create a user with no solicitudes
        empty_user = User.objects.create_user(
            username='empty_user',
            email='empty@example.com',
            password='testpassword123'
        )
        
        # Log in as the empty user
        self.client.login(username='empty_user', password='testpassword123')
        
        # Get the solicitudes page
        response = self.client.get(reverse('donaredapp:solicitudes'))
        
        # Check response status code
        self.assertEqual(response.status_code, 200)
        
        # Check that the solicitudes list is empty
        self.assertEqual(len(response.context['solicitudes']), 0)

class DonacionesViewTest(TestCase):
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
        
        self.otro_donante = User.objects.create_user(
            username='otro_donante',
            email='otro_donante@example.com',
            password='testpassword123'
        )
        
        # Create test zona, categoria, and items
        self.zona = Zona.objects.create(nombre='CABA')
        self.categoria = Categoria.objects.create(nombre='Muebles')
        
        # Active items for donante
        self.item1 = Item.objects.create(
            nombre='Mesa',
            descripcion='Una mesa',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.donante,
            activo=True
        )
        
        self.item2 = Item.objects.create(
            nombre='Silla',
            descripcion='Una silla',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.donante,
            activo=True
        )
        
        # Inactive item for donante
        self.item_inactive = Item.objects.create(
            nombre='Lámpara',
            descripcion='Una lámpara',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.donante,
            activo=False
        )
        
        # Item for otro_donante
        self.item_otro = Item.objects.create(
            nombre='Estantería',
            descripcion='Una estantería',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.otro_donante,
            activo=True
        )
        
        # Create solicitudes with different dates to test ordering
        # Older solicitud
        self.solicitud1 = Solicitud.objects.create(
            item=self.item1,
            beneficiario=self.beneficiario,
            donante=self.donante,
            fecha_creacion=timezone.now() - timezone.timedelta(days=2)
        )
        
        # Newer solicitud
        self.solicitud2 = Solicitud.objects.create(
            item=self.item2,
            beneficiario=self.beneficiario,
            donante=self.donante,
            fecha_creacion=timezone.now() - timezone.timedelta(days=1)
        )
        
        # Solicitud for otro_donante
        self.solicitud_otro = Solicitud.objects.create(
            item=self.item_otro,
            beneficiario=self.beneficiario,
            donante=self.otro_donante,
            fecha_creacion=timezone.now()
        )
        
        # Set up client
        self.client = Client()
    
    def test_donaciones_view_authenticated(self):
        """Test that authenticated users can access their donaciones"""
        # Log in as donante
        self.client.login(username='donante', password='testpassword123')
        
        # Get the donaciones page
        response = self.client.get(reverse('donaredapp:donaciones'))
        
        # Check response status code
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct template is used
        self.assertTemplateUsed(response, 'donaredapp/donaciones.html')
        
        # Check that both items and solicitudes are in the context
        self.assertIn('items', response.context)
        self.assertIn('solicitudes', response.context)
        
        # Check that only active items are returned
        self.assertEqual(len(response.context['items']), 2)
        self.assertIn(self.item1, response.context['items'])
        self.assertIn(self.item2, response.context['items'])
        self.assertNotIn(self.item_inactive, response.context['items'])
        
        # Check that both solicitudes are returned
        self.assertEqual(len(response.context['solicitudes']), 2)
        
        # Check that the solicitudes are ordered by fecha_creacion in descending order
        # (newest first)
        self.assertEqual(response.context['solicitudes'][0], self.solicitud2)
        self.assertEqual(response.context['solicitudes'][1], self.solicitud1)
    
    def test_donaciones_view_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        # Access the donaciones page without being logged in
        response = self.client.get(reverse('donaredapp:donaciones'))
        
        # Check that user is redirected to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
    
    def test_donaciones_view_different_user(self):
        """Test that a user only sees their own items and solicitudes"""
        # Log in as otro_donante
        self.client.login(username='otro_donante', password='testpassword123')
        
        # Get the donaciones page
        response = self.client.get(reverse('donaredapp:donaciones'))
        
        # Check response status code
        self.assertEqual(response.status_code, 200)
        
        # Check that only otro_donante's items are returned
        items = response.context['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], self.item_otro)
        
        # Check that only otro_donante's solicitudes are returned
        solicitudes = response.context['solicitudes']
        self.assertEqual(len(solicitudes), 1)
        self.assertEqual(solicitudes[0], self.solicitud_otro)
    
    def test_empty_donaciones(self):
        """Test behavior when a user has no items or solicitudes"""
        # Create a user with no items or solicitudes
        empty_user = User.objects.create_user(
            username='empty_user',
            email='empty@example.com',
            password='testpassword123'
        )
        
        # Log in as the empty user
        self.client.login(username='empty_user', password='testpassword123')
        
        # Get the donaciones page
        response = self.client.get(reverse('donaredapp:donaciones'))
        
        # Check response status code
        self.assertEqual(response.status_code, 200)
        
        # Check that the items and solicitudes lists are empty
        self.assertEqual(len(response.context['items']), 0)
        self.assertEqual(len(response.context['solicitudes']), 0)
    
    def test_inactive_items_not_shown(self):
        """Test that inactive items are not shown in the donaciones view"""
        # Create an inactive item
        inactive_item = Item.objects.create(
            nombre='Sofá',
            descripcion='Un sofá',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.donante,
            activo=False
        )
        
        # Log in as donante
        self.client.login(username='donante', password='testpassword123')
        
        # Get the donaciones page
        response = self.client.get(reverse('donaredapp:donaciones'))
        
        # Check that inactive items are not included
        items = response.context['items']
        self.assertNotIn(inactive_item, items)
        self.assertNotIn(self.item_inactive, items)
    
class GestionarSolicitudTest(TestCase):
    def setUp(self):
        # Create test users
        self.donante = User.objects.create_user(
            username='donante',
            email='donante@example.com',
            password='testpassword123'
        )
        
        self.beneficiario1 = User.objects.create_user(
            username='beneficiario1',
            email='beneficiario1@example.com',
            password='testpassword123'
        )
        
        self.beneficiario2 = User.objects.create_user(
            username='beneficiario2',
            email='beneficiario2@example.com',
            password='testpassword123'
        )
        
        self.otro_donante = User.objects.create_user(
            username='otro_donante',
            email='otro_donante@example.com',
            password='testpassword123'
        )
        
        # Create test zona, categoria, and items
        self.zona = Zona.objects.create(nombre='CABA')
        self.categoria = Categoria.objects.create(nombre='Muebles')
        
        self.item1 = Item.objects.create(
            nombre='Mesa',
            descripcion='Una mesa',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.donante,
            activo=True
        )
        
        self.item2 = Item.objects.create(
            nombre='Silla',
            descripcion='Una silla',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.donante,
            activo=True
        )
        
        self.item_otro = Item.objects.create(
            nombre='Estantería',
            descripcion='Una estantería',
            zona=self.zona,
            categoria=self.categoria,
            usuario=self.otro_donante,
            activo=True
        )
        
        # Create solicitudes
        self.solicitud1 = Solicitud.objects.create(
            item=self.item1,
            beneficiario=self.beneficiario1,
            donante=self.donante,
            estado='PENDIENTE',
            fecha_creacion=timezone.now()
        )
        
        # Another solicitud for the same item from different beneficiary
        self.solicitud_mismoitem = Solicitud.objects.create(
            item=self.item1,
            beneficiario=self.beneficiario2,
            donante=self.donante,
            estado='PENDIENTE',
            fecha_creacion=timezone.now()
        )
        
        self.solicitud2 = Solicitud.objects.create(
            item=self.item2,
            beneficiario=self.beneficiario1,
            donante=self.donante,
            estado='PENDIENTE',
            fecha_creacion=timezone.now()
        )
        
        self.solicitud_otro = Solicitud.objects.create(
            item=self.item_otro,
            beneficiario=self.beneficiario1,
            donante=self.otro_donante,
            estado='PENDIENTE',
            fecha_creacion=timezone.now()
        )
        
        # Set up client
        self.client = Client()
    
    def test_gestionar_solicitud_aceptar(self):
        """Test accepting a request"""
        # Log in as donante
        self.client.login(username='donante', password='testpassword123')
        
        # Accept the solicitud1
        response = self.client.post(
            reverse('donaredapp:gestionar_solicitud', kwargs={'solicitud_id': self.solicitud1.id}),
            {'action': 'aceptar'}
        )
        
        # Check that we are redirected to donaciones
        self.assertRedirects(response, reverse('donaredapp:donaciones'))
        
        # Refresh the solicitud from the database
        self.solicitud1.refresh_from_db()
        
        # Check that the solicitud state has been updated
        self.assertEqual(self.solicitud1.estado, 'ACEPTADA')
        
        # Check that a success message was added
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(f"Has aceptado la solicitud de {self.beneficiario1.username}", str(messages[0]))
        
        # Check that the item is still active
        self.item1.refresh_from_db()
        self.assertTrue(self.item1.activo)
        
        # Check that other solicitudes for this item remain PENDIENTE
        self.solicitud_mismoitem.refresh_from_db()
        self.assertEqual(self.solicitud_mismoitem.estado, 'PENDIENTE')
    
    def test_gestionar_solicitud_rechazar(self):
        """Test rejecting a request"""
        # Log in as donante
        self.client.login(username='donante', password='testpassword123')
        
        # Reject the solicitud1
        response = self.client.post(
            reverse('donaredapp:gestionar_solicitud', kwargs={'solicitud_id': self.solicitud1.id}),
            {'action': 'rechazar'}
        )
        
        # Check that we are redirected to donaciones
        self.assertRedirects(response, reverse('donaredapp:donaciones'))
        
        # Refresh the solicitud from the database
        self.solicitud1.refresh_from_db()
        
        # Check that the solicitud state has been updated
        self.assertEqual(self.solicitud1.estado, 'RECHAZADA')
        
        # Check that a success message was added
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(f"Has rechazado la solicitud de {self.beneficiario1.username}", str(messages[0]))
        
        # Check that the item is still active
        self.item1.refresh_from_db()
        self.assertTrue(self.item1.activo)
        
        # Check that other solicitudes for this item remain PENDIENTE
        self.solicitud_mismoitem.refresh_from_db()
        self.assertEqual(self.solicitud_mismoitem.estado, 'PENDIENTE')

    def test_gestionar_solicitud_completar(self):
        """Test completing a request"""
        # Log in as donante
        self.client.login(username='donante', password='testpassword123')
        
        # Complete the solicitud1
        response = self.client.post(
            reverse('donaredapp:gestionar_solicitud', kwargs={'solicitud_id': self.solicitud1.id}),
            {'action': 'completar'}
        )
        
        # Check that we are redirected to donaciones
        self.assertRedirects(response, reverse('donaredapp:donaciones'))
        
        # Refresh the solicitud from the database
        self.solicitud1.refresh_from_db()
        
        # Check that the solicitud state has been updated
        self.assertEqual(self.solicitud1.estado, 'COMPLETADA')
        
        # Check that the item is now inactive
        self.item1.refresh_from_db()
        self.assertFalse(self.item1.activo)
        
        # Check that other solicitudes for this item have been RECHAZADA
        self.solicitud_mismoitem.refresh_from_db()
        self.assertEqual(self.solicitud_mismoitem.estado, 'RECHAZADA')
        
        # Check that solicitudes for other items remain PENDIENTE
        self.solicitud2.refresh_from_db()
        self.assertEqual(self.solicitud2.estado, 'PENDIENTE')
        
        # Check that a success message was added
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(f"Has completado la donación de {self.item1.nombre}", str(messages[0]))
    
    def test_gestionar_solicitud_other_user(self):
        """Test that a user cannot manage another user's solicitudes"""
        # Log in as otro_donante
        self.client.login(username='otro_donante', password='testpassword123')
        
        # Try to accept solicitud1 which belongs to donante
        response = self.client.post(
            reverse('donaredapp:gestionar_solicitud', kwargs={'solicitud_id': self.solicitud1.id}),
            {'action': 'aceptar'}
        )
        
        # Check that we get a 404 response
        self.assertEqual(response.status_code, 404)
        
        # Refresh the solicitud from the database
        self.solicitud1.refresh_from_db()
        
        # Check that the solicitud state has not changed
        self.assertEqual(self.solicitud1.estado, 'PENDIENTE')
    
    def test_gestionar_solicitud_unauthenticated(self):
        """Test that unauthenticated users cannot manage solicitudes"""
        # Try to accept solicitud1 without being logged in
        response = self.client.post(
            reverse('donaredapp:gestionar_solicitud', kwargs={'solicitud_id': self.solicitud1.id}),
            {'action': 'aceptar'}
        )
        
        # Check that user is redirected to login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
        
        # Refresh the solicitud from the database
        self.solicitud1.refresh_from_db()
        
        # Check that the solicitud state has not changed
        self.assertEqual(self.solicitud1.estado, 'PENDIENTE')
    
    def test_gestionar_solicitud_invalid_action(self):
        """Test behavior with invalid action"""
        # Log in as donante
        self.client.login(username='donante', password='testpassword123')
        
        # Send an invalid action
        response = self.client.post(
            reverse('donaredapp:gestionar_solicitud', kwargs={'solicitud_id': self.solicitud1.id}),
            {'action': 'invalid_action'}
        )
        
        # Check that we are redirected to donaciones
        self.assertRedirects(response, reverse('donaredapp:donaciones'))
        
        # Refresh the solicitud from the database
        self.solicitud1.refresh_from_db()
        
        # Check that the solicitud state has not changed
        self.assertEqual(self.solicitud1.estado, 'PENDIENTE')
        
        # Check that no message was added
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)
    
    def test_gestionar_solicitud_get_request(self):
        """Test GET request to the view (should just redirect)"""
        # Log in as donante
        self.client.login(username='donante', password='testpassword123')
        
        # Make a GET request
        response = self.client.get(
            reverse('donaredapp:gestionar_solicitud', kwargs={'solicitud_id': self.solicitud1.id})
        )
        
        # Check that we are redirected to donaciones
        self.assertRedirects(response, reverse('donaredapp:donaciones'))
        
        # Refresh the solicitud from the database
        self.solicitud1.refresh_from_db()
        
        # Check that the solicitud state has not changed
        self.assertEqual(self.solicitud1.estado, 'PENDIENTE')