from django import forms
from finance.models import FinanceRecord

class FinanceRecordForm(forms.ModelForm):
    class Meta:
        model = FinanceRecord
        fields = ("category","amount","description")


