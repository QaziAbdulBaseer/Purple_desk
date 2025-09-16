from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ADMIN = 'admin'
    BOT = 'bot'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (BOT, 'Bot'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=BOT)

    def __str__(self):
        return f"{self.username} ({self.role})"  