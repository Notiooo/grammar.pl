from django import forms
from django.core.mail import send_mail

from secret_settings import secret_email_contacts_list

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True, label="Podaj swój email")
    title = forms.CharField(required=True, max_length=60, label="Tytuł wiadomości")
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': '10', 'style':'resize:none;'}), required=True, max_length=600, label="Wpisz swoją wiadomość")

    def send_email(self):
        send_mail(
            self.cleaned_data['title'],
            self.cleaned_data['message'],
            self.cleaned_data['from_email'],
            secret_email_contacts_list,
        )
        pass