from django.db import models
from django.contrib.auth.models import User

class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    fecha = models.DateField(auto_now_add=True)
    contenido = models.TextField()
    imagen = models.ImageField(upload_to='noticias/', blank=True, null=True)
    tendencia = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

class Comentario(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.autor.username} - {self.noticia.titulo}'

class RegistroBelico(models.Model):
    familia1 = models.CharField(max_length=100)
    familia2 = models.CharField(max_length=100)
    ganador = models.CharField(max_length=100)
    fecha = models.DateField()

    def __str__(self):
        return f'{self.familia1} vs {self.familia2}'

class RankingFamilia(models.Model):
    familia = models.CharField(max_length=100)
    pettadas = models.IntegerField(default=0)

    class Meta:
        ordering = ['-pettadas']

    def __str__(self):
        return self.familia

class Familia(models.Model):
    nombre = models.CharField(max_length=100)
    don = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre