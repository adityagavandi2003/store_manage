from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.

def uid():
    idd = uuid.uuid4()
    # Convert UUID to string before splitting
    sp = str(idd).split('-')
    return f'#SALE00{sp[0]+sp[1]}'

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
    report_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.report_id