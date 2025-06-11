from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    movil = PhoneNumberField(blank=True, null=True, region='AR')
    validado = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"

# Create a Profile for each new User automatically
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Resena(models.Model):
    ESTADO_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]
    
    solicitud = models.OneToOneField('Solicitud', on_delete=models.CASCADE, related_name='resena')
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de 1 a 5 estrellas"
    )
    comentario = models.TextField(max_length=500, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='pending',
        help_text="Estado de la reseña"
    )
    
    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Reseña de {self.solicitud.beneficiario.username} para {self.solicitud.donante.username}"
    
    @property
    def estrellas(self):
        """Retorna la calificación en formato de estrellas"""
        return '★' * self.calificacion + '☆' * (5 - self.calificacion)

class Categoria(models.Model):
    nombre = models.CharField(max_length=25)

    def __str__(self):
        return self.nombre
    
class Item(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=500)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='items',
        null=True,
    )
    imagen = models.ImageField(upload_to='items/', null=True, blank=True, default='items/sin_imagen.png')
    domicilio = models.CharField(max_length=255, null=True, blank=True)
    activo = models.BooleanField(default=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.nombre
    
class Solicitud(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_solicitudes')
    donante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donante_solicitudes')
    beneficiario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='beneficiario_solicitudes')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADA', 'Aceptada'),
        ('RECHAZADA', 'Rechazada'),
        ('CONCRETADA', 'Concretada'),
    ]
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDIENTE')
    
    class Meta:
        # Avoid duplicate requests for the same item from the same user
        unique_together = ['item', 'beneficiario']
        verbose_name = 'Donación'
        verbose_name_plural = 'Donaciones'
    
    def __str__(self):
        return f"Donación de {self.item.nombre}, ofrecida por {self.donante.username}, solicitada por {self.beneficiario.username}"