from django import forms
from phonebook.models import AddContact

class ContactAddForm(forms.ModelForm): 
    class Meta:
        model = AddContact
        fields = ["name",'phone_number']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')

        if self.request and self.request.user.is_authenticated:
            # Only check if the number is already saved by the same shop
            if AddContact.objects.filter(phone_number=phone, shop=self.request.user).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This phone number is already in your contacts.")

        return phone