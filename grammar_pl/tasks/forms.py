from django import forms
from django.core.mail import send_mail
from . import models
from django.forms.models import inlineformset_factory
import time
from secret_settings import secret_email_contacts_list
from django.core.cache import cache
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3


class ContactForm(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaV3, error_messages={
        'required': 'Wystąpił problem z RECAPTCHA. Spróbuj jeszcze raz... chyba, że jesteś robotem 🤔', })

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


class QuestionForm(forms.ModelForm):
    class Meta:
        model = models.Question
        exclude = ()


class AnwserForm(forms.ModelForm):
    class Meta:
        model = models.Anwser
        exclude = ()


# ----- Question formsets -----

QuestionFormSet = inlineformset_factory(
    models.Task, models.Question, form=QuestionForm,
    fields=['text',], extra=0, max_num=16, min_num=1, labels={'text': 'Pytanie'}, can_delete=True)


# ------ Anwser formsets -------

AnwserFormSet = inlineformset_factory(
    models.Question, models.Anwser, form=AnwserForm,
    fields=['text', 'correct'],
    widgets={'text': forms.TextInput(attrs={'class': 'uk-input'}),
             'correct': forms.CheckboxInput(attrs={'class': 'uk-checkbox uk-padding-small'})},
    labels={'text': 'Odpowiedź',
            'correct': 'Czy to poprawna odpowiedź?'},
    extra=1, max_num=6,
    min_num=0, can_delete=True)

AnwserFormSet_FillGaps = inlineformset_factory(
    models.Question, models.Anwser, form=AnwserForm,
    fields=['text',],
    widgets={'text': forms.TextInput(attrs={'class': 'uk-input'})},
    labels={'text': 'Możliwe odpowiedzi'},
    extra=1, max_num=6,
    min_num=0, can_delete=True)


class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ['category', 'title', 'text', 'source']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }


class TaskCreateForm(forms.ModelForm):
    time_between_tasks = 240
    action = 'add_task'

    class Meta:
        model = models.Task
        fields = ['category', 'title', 'text', 'source']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        username = self.cleaned_data.get('username')
        cache_results = ActionTimeout.get(self.action, username)
        now = time.time()
        last_attempt = cache_results['last_attempt'] if cache_results else False
        if last_attempt > (now - self.time_between_tasks):
            raise forms.ValidationError(
                'Poczekaj chwile! Zbyt szybko dodajesz zadania. Odczekaj między nimi %(seconds)s sekund. Wykorzystaj ten czas na wymyślenie dobrego zadania. Przepraszamy za utrudnienia! 😭',
                params={'seconds': self.time_between_tasks})
        return super(TaskCreateForm, self).clean()

    def save(self, commit=True):
        ActionTimeout.set(self.action, self.cleaned_data.get('username'), time.time())
        return super(TaskCreateForm, self).save()


class CommentForm(forms.ModelForm):
    time_between_comments = 30  # in seconds
    action = 'add_comment'

    class Meta:
        model = models.Comment
        fields = ['text']

    def clean(self):
        username = self.cleaned_data.get('username')
        cache_results = ActionTimeout.get(self.action, username)
        now = time.time()
        # gets last attempt or create one
        last_attempt = cache_results['last_attempt'] if cache_results else False

        if last_attempt > (now - self.time_between_comments):
            raise forms.ValidationError(
                'Poczekaj chwile! Zbyt szybko dodajesz komentarze. Odczekaj między nimi %(seconds)s sekund.',
                params={'seconds': self.time_between_comments})
        return super(CommentForm, self).clean()

    def save(self):
        ActionTimeout.set(self.action, self.cleaned_data.get('username'), time.time())
        return super(CommentForm, self).save()


class ActionTimeout:
    """
    It is used in situations where a certain action of a user should not be allowed to do infinite amount of times
    So it's a kind of time block between every signle action
    """
    @staticmethod
    def _key(action, username):
        return '{}_timeout_{}'.format(action, username)

    @staticmethod
    def _value(time):
        return {
            'last_attempt': time,
        }

    @staticmethod
    def delete(action, username):
        cache.delete(ActionTimeout._key(action, username))

    @staticmethod
    def set(action, username, time):
        key = ActionTimeout._key(action, username)
        value = ActionTimeout._value(time)
        cache.set(key, value)

    @staticmethod
    def get(action, username):
        key = ActionTimeout._key(action, username)
        return cache.get(key)


class TaskReport_Form(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': '10', 'style': 'resize:none;'}), required=True,
                              help_text="Opisz szczegółowo problem", max_length=600, label="Wpisz swoją wiadomość")
    email = forms.EmailField(required=False, help_text="Opcjonalnie, jeżeli spodziewasz otrzymać się odpowiedź",
                             label="Adres email")

    def send_email(self, id):
        send_mail(
            '[PROBLEM] ID: {0} - zadania społeczności'.format(id),
            self.cleaned_data['message'],
            self.cleaned_data['email'],
            secret_email_contacts_list,
        )
