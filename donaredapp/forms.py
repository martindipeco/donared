from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Item
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from django.core.exceptions import ValidationError

class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration with additional fields
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    movil = forms.IntegerField(
        required=False,
        min_value=1000000000,  # Minimum 10 digits
        max_value=999999999999999,  # Maximum 15 digits
        help_text="Solo números (ej: 5411123456789)",
        widget=forms.NumberInput(attrs={
            'placeholder': '5411123456789',
            'class': 'form-control'
        })
    )
    validado = forms.BooleanField(
        required=False,
        label="Quiero ser validado para recibir donaciones",
        help_text="Marca esta casilla para habilitar recibir donaciones tras validación."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'movil', 'validado', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            # Save the mobile number to the user's profile
            user.profile.movil = self.cleaned_data['movil']
            #user.profile.validado = self.cleaned_data['validado']
            user.profile.save()
        return user
    
class UserEditForm(forms.ModelForm):
    """
    Form for editing basic User information
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombre'
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Apellido'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label='Email'
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Nombre de usuario',
        help_text='Requerido. 150 caracteres o menos. Solo letras, dígitos y @/./+/-/_'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_username(self):
        username = self.cleaned_data['username']
        # Check if username exists and is not the current user's username
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if email exists and is not the current user's email
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email
    
class ProfileEditForm(forms.ModelForm):
    """
    Form for editing Profile information (movil and validado)
    """
    movil = forms.IntegerField(
        required=False,
        min_value=1000000000,  # Minimum 10 digits
        max_value=999999999999999,  # Maximum 15 digits
        help_text="Solo números (ej: 5411123456789)",
        widget=forms.NumberInput(attrs={
            'placeholder': '5411123456789',
            'class': 'form-control'
        }),
        label='Número de móvil (opcional)'
    )
    validado = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Quiero ser validado para recibir donaciones',
        help_text='Marca esta casilla para habilitar recibir donaciones tras validación.'
    )

    class Meta:
        model = Profile
        fields = ['movil', 'validado']
    
class PasswordRecoveryForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'id_email'})
    )

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['nombre', 'descripcion', 'zona', 'categoria', 'domicilio', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'zona': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        domicilio = cleaned_data.get('domicilio')
        zona = cleaned_data.get('zona')
        categoria = cleaned_data.get('categoria')

        # Validar zona
        if not zona:
            raise ValidationError({'zona': 'Debe seleccionar una zona'})
        
        # Validar categoría
        if not categoria:
            raise ValidationError({'categoria': 'Debe seleccionar una categoría'})

        # Validar domicilio usando OpenStreetMap
        if domicilio:
            try:
                # Usar RateLimiter para evitar problemas con la API
                geolocator = RateLimiter(Nominatim(user_agent="donared"), min_delay_seconds=1)
                location = geolocator.geocode(domicilio)
                
                if location is None:
                    raise ValidationError({'domicilio': 'Domicilio incorrecto, vuelva a cargalo'})
                
                # Guardar las coordenadas
                cleaned_data['latitude'] = location.latitude
                cleaned_data['longitude'] = location.longitude
                
            except Exception as e:
                raise ValidationError({'domicilio': 'Error al validar el domicilio: ' + str(e)})
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Asignar las coordenadas si están en cleaned_data
        if 'latitude' in self.cleaned_data:
            instance.latitude = self.cleaned_data['latitude']
        if 'longitude' in self.cleaned_data:
            instance.longitude = self.cleaned_data['longitude']
        
        if commit:
            instance.save()
        return instance