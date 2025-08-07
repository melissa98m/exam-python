from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Modèle pour représenter un user.
    """
    email = models.EmailField(unique=True) # Email unique

class Project(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True) # Description optionnelle
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects') # Suppression en cascade si owner supprimé

    def __str__(self):
        return self.title
