from django import forms
from django.core.mail import send_mail
from . import models
from django.forms.models import inlineformset_factory, BaseInlineFormSet

from secret_settings import secret_email_contacts_list


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True, label="Podaj swój email")
    title = forms.CharField(required=True, max_length=60, label="Tytuł wiadomości")
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': '10', 'style': 'resize:none;'}), required=True,
                              max_length=600, label="Wpisz swoją wiadomość")

    def send_email(self):
        send_mail(
            self.cleaned_data['title'],
            self.cleaned_data['message'],
            self.cleaned_data['from_email'],
            secret_email_contacts_list,
        )
        pass


class QuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
        exclude = ()


class AnwserForm(forms.ModelForm):
    class Meta:
        model = models.Anwser
        exclude = ()


QuestionFormSet = inlineformset_factory(
    models.Task, models.Question, form=QuestionForm,
    fields=['text'], extra=0, max_num=3, min_num=1, labels={'text': 'Pytanie'}, can_delete=True)

AnwserFormSet = inlineformset_factory(
    models.Question, models.Anwser, form=AnwserForm,
    fields=['text', 'correct'],
    widgets={'text': forms.TextInput(attrs={'class': 'uk-input'}),
             'correct': forms.CheckboxInput(attrs={'class': 'uk-checkbox uk-padding-small'})},
    labels={'text': 'Odpowiedź',
            'correct': 'Czy to poprawna odpowiedź?'},
    extra=1, max_num=3,
    min_num=0, can_delete=True)


class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ['category', 'title', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }
