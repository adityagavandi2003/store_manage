from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class AddContact(models.Model):
    shop = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    