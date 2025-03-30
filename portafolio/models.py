from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Client(models.Model):
    user = models.OneToOneField(
    User, on_delete=models.CASCADE, null=True, blank=True)
    celular = models.CharField(max_length=15, null=True, blank=True)