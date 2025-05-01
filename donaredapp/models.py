from django.db import models

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

    def __str__(self):
        return self.nombre