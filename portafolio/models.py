from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Client(models.Model):
    user = models.OneToOneField(
    User, on_delete=models.CASCADE, null=True, blank=True)
    celular = models.CharField(max_length=15, null=True, blank=True)

class Project(models.Model):
    nombre = models.CharField(max_length=100)
    empresa = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} - {self.empresa}"
    
class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} - {self.content[:50]}'
