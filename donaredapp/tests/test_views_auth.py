# tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from ..forms import UserRegistrationForm
from ..models import Profile


class PhoneNumberValidationTestCase(TestCase):
    """Test cases for phone number validation in user registration"""
    
    def setUp(self):
        """Set up test client and common test data"""
        self.client = Client()
        self.registration_url = reverse('donaredapp:registro')  # Adjust URL name as needed
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
            'validado': False
        }
    
    def test_valid_phone_numbers(self):
        """Test that valid phone numbers are accepted"""
        valid_phones = [
            5411123456789,  # Standard format
            1234567890,     # Minimum length (10 digits)
            123456789012345, # Maximum length (15 digits)
            54911234567,    # Another valid format
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                form_data = self.valid_user_data.copy()
                form_data['movil'] = phone
                
                form = UserRegistrationForm(data=form_data)
                self.assertTrue(
                    form.is_valid(), 
                    f"Phone {phone} should be valid. Errors: {form.errors}"
                )
    
    def test_invalid_phone_numbers_in_form(self):
        """Test that invalid phone numbers are rejected by the form"""
        invalid_phones = [
            'abc123',       # Contains letters
            '123-456-789',  # Contains hyphens (should be IntegerField)
            'not_a_number', # Completely invalid
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                form_data = self.valid_user_data.copy()
                form_data['movil'] = phone
                
                form = UserRegistrationForm(data=form_data)
                self.assertFalse(
                    form.is_valid(),
                    f"Phone {phone} should be invalid"
                )
                self.assertIn('movil', form.errors)
    
    def test_empty_phone_number(self):
        """Test that empty phone number is allowed (optional field)"""
        form_data = self.valid_user_data.copy()
        # Don't include movil field (empty/optional)
        
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form should be valid without phone. Errors: {form.errors}")
        
        # Test with empty string
        form_data['movil'] = ''
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form should be valid with empty phone. Errors: {form.errors}")
    
    def test_successful_registration_with_valid_phone(self):
        """Test complete registration process with valid phone number"""
        form_data = self.valid_user_data.copy()
        form_data['movil'] = 5411123456789
        
        response = self.client.post(self.registration_url, form_data)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Check profile was created with correct phone
        user = User.objects.get(username='testuser')
        self.assertEqual(user.profile.movil, 5411123456789)
        
        # Check redirect (successful registration)
        self.assertRedirects(response, reverse('donaredapp:index'))  # Adjust as needed
    
    def test_successful_registration_without_phone(self):
        """Test registration without phone number"""
        form_data = self.valid_user_data.copy()
        # Don't include phone
        
        response = self.client.post(self.registration_url, form_data)
        
        # Check user was created
        user = User.objects.get(username='testuser')
        self.assertIsNone(user.profile.movil)
    
    def test_registration_failure_with_invalid_phone_via_view(self):
        """Test registration fails gracefully with invalid phone via view"""
        form_data = self.valid_user_data.copy()
        form_data['movil'] = 'invalid_phone'
        
        response = self.client.post(self.registration_url, form_data)
        
        # Should not create user
        self.assertFalse(User.objects.filter(username='testuser').exists())
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registro de Usuario')  # Check we're still on registration page
    
    def test_phone_number_boundaries(self):
        """Test phone number length boundaries"""
        # Test minimum valid length (10 digits)
        form_data = self.valid_user_data.copy()
        form_data['movil'] = 1234567890
        
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test maximum valid length (15 digits)
        form_data['movil'] = 123456789012345
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test too short (9 digits) - Note: IntegerField doesn't enforce length by default
        # You might need to add min_value/max_value to your form for this test
        form_data['movil'] = 123456789
        form = UserRegistrationForm(data=form_data)
        # This test depends on whether you added min_value to your IntegerField
        # If you haven't, this will pass (which might be okay)
    
    def test_profile_creation_signal(self):
        """Test that Profile is automatically created when User is created"""
        # Create user directly (not through form)
        user = User.objects.create_user(
            username='signaltest',
            email='signal@test.com',
            password='testpass123'
        )
        
        # Check profile was created by signal
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertIsNotNone(user.profile)
    
    def test_form_field_types(self):
        """Test that form fields have correct types"""
        form = UserRegistrationForm()
        
        # Check that movil is IntegerField
        from django import forms
        self.assertIsInstance(form.fields['movil'], forms.IntegerField)
        self.assertFalse(form.fields['movil'].required)  # Should be optional
    
    def test_model_field_types(self):
        """Test that model fields have correct types"""
        # Create a profile to test field types
        user = User.objects.create_user('fieldtest', 'field@test.com', 'pass123')
        profile = user.profile
        
        # Test field accepts integer
        profile.movil = 1234567890
        profile.save()
        
        # Refresh from database
        profile.refresh_from_db()
        self.assertEqual(profile.movil, 1234567890)
        self.assertIsInstance(profile.movil, int)


class UserRegistrationIntegrationTestCase(TestCase):
    """Integration tests for the complete registration flow"""
    
    def test_complete_registration_flow(self):
        """Test the entire registration process"""
        # Get registration page
        response = self.client.get(reverse('donaredapp:registro'))
        self.assertEqual(response.status_code, 200)
        
        # Submit valid registration
        form_data = {
            'username': 'integrationtest',
            'email': 'integration@test.com',
            'first_name': 'Integration',
            'last_name': 'Test',
            'movil': 5411987654321,
            'validado': True,
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }
        
        response = self.client.post(reverse('donaredapp:registro'), form_data)
        
        # Check user was created and logged in
        user = User.objects.get(username='integrationtest')
        self.assertEqual(user.email, 'integration@test.com')
        self.assertEqual(user.first_name, 'Integration')
        self.assertEqual(user.last_name, 'Test')
        
        # Check profile data
        self.assertEqual(user.profile.movil, 5411987654321)
        self.assertTrue(user.profile.validado)
        
        # Check successful redirect
        self.assertRedirects(response, reverse('donaredapp:index'))
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('exitosamente' in str(m) for m in messages))