from items.models import Product
from django.dispatch import Signal,receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from users.models import Notification

notifications = Signal()

@receiver(notifications)
def notification(sender,*args, **kwargs):
    print('----------------------------------')
    print('Notification')
    print(sender)
    print({kwargs})


