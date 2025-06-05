from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    movil = models.PositiveBigIntegerField(blank=True, null=True)
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

class Categoria(models.Model):
    nombre = models.CharField(max_length=25)

    def __str__(self):
        return self.nombre
    
class Item(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
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