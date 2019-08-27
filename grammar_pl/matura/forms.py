from django import forms
from .models import Matura_Anwser
from django.core.mail import send_mail
from django.shortcuts import reverse

from secret_settings import secret_email_contacts_list


class Matura_Task_Anwser_Form(forms.ModelForm):
    # anwser = forms.ModelMultipleChoiceField(queryset=Matura_Task.anwser.objects.all())
    class Meta:
        model = Matura_Anwser
        fields = '__all__'


class MaturaReport_Form(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': '10', 'style': 'resize:none;'}), required=True,
                              help_text="Opisz szczegółowo problem", max_length=600, label="Wpisz swoją wiadomość")
    email = forms.EmailField(required=False, help_text="Opcjonalnie, jeżeli spodziewasz otrzymać się odpowiedź",
                             label="Adres email")

    def send_email(self, id):
        send_mail(
            '[PROBLEM] ID: {}'.format(id),
            self.cleaned_data['message'],
            self.cleaned_data['email'],
            secret_email_contacts_list,
        )
