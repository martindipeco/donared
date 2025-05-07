from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    movil = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

# Create a Profile for each new User automatically
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Zona(models.Model):

    ZONA_CHOICES = [
        ('CABA', 'CABA'),
        ('NORTE', 'Norte'),
        ('SUR', 'Sur'),
        ('OESTE', 'Oeste'),
    ]

    nombre = models.CharField(max_length=20, choices=ZONA_CHOICES)

    def __str__(self):
        return self.nombre
    

class Categoria(models.Model):

    nombre = models.CharField(max_length=25)

    def __str__(self):
        return self.nombre
    

class Item(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='items',
        null=True,  # Allow null for compatibility with existing items
    )
    imagen = models.ImageField(upload_to='items/', null=True, blank=True)
    activo = models.BooleanField(default=True)

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
    
    def __str__(self):
        return f"Solicitud de {self.beneficiario.username} para {self.item.nombre} ofrecido por {self.donante.username}"