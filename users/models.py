from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
# Create your models here.

def uid():
    idd = uuid.uuid4()
    sp = str(idd).split('-')
    return f'{sp[0]+sp[1]+sp[3]}'

report = [
    ("Bug Report","Bug Report"),
    ('Feature Request','Feature Request'),
    ('General Suggestion','General Suggestion'),
    ('Complaint','Complaint'),
    ('Praise','Praise'),
    ('Other','Other')
]

class Report(models.Model):
    report_id = models.CharField(primary_key=True, default=uid, editable=False,max_length=255)
    report_by = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(choices=report, max_length=50)
    subject = models.CharField(max_length=50,null=True,blank=True)
    report = models.TextField(null=True,blank=True)
    is_solved = models.BooleanField(default=False)
    report_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.report_id
    

class Notification(models.Model):
    TYPE_CHOICES = (
        ('stock', 'Stock Alert'),
        ('turnover', 'Monthly Turnover'),
        ('info', 'General Info'),
        ('greet', 'Greet'),
        ('update', 'Update'),
    )
    shop = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE) 
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read_by = models.ManyToManyField(User, related_name='read_notifications', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.notification_type.title()} - {self.message[:30]}"
