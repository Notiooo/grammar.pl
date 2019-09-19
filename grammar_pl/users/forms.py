from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django import forms
from .models import CustomUser
import time
import requests
from django.conf import settings

from django.core.cache import cache


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    avatar = forms.ImageField(required=False, widget=forms.FileInput)

    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('email', 'about', 'birth', 'first_name', 'last_name', 'avatar')


class CustomAuthenticationForm(AuthenticationForm):
    invalid_attempt_time = 5  # in minutes

    def clean(self):
        ip_address = self.request.META['REMOTE_ADDR']
        cache_results = InvalidLoginAttemptsCache.get(ip_address)
        now = time.time()
        # gets a list of invalid attempts, or create empty one
        invalid_attempt_timestamps = cache_results['invalid_attempt_timestamps'] if cache_results else []

        # clear any invalid login attempts from the timestamp bucket that were longer ago than the range
        invalid_attempt_timestamps = [timestamp for timestamp in invalid_attempt_timestamps if
                                      timestamp > (now - self.invalid_attempt_time * 60)]  # 5 minutes (5 * 60 sec)

        # adds this attempt as an invalid (cause if it's correct then it's gonna delete cache anyway
        invalid_attempt_timestamps.append(now)
        # if there are more than 5 invalid attempts then raise an error
        if len(invalid_attempt_timestamps) >= 5:
            raise forms.ValidationError('Wykorzystałeś limit prób logowania 😥 - spróbuj ponownie za 5 minut',
                                        code='invalid_login')
        InvalidLoginAttemptsCache.set(ip_address, invalid_attempt_timestamps, now)
        return super(CustomAuthenticationForm, self).clean()

    def confirm_login_allowed(self, user):
        secret_key = settings.RECAPTCHA_SECRET_KEY

        # captcha verification
        data = {
            'response': self.request.POST.get('g-recaptcha-response'),
            'secret': secret_key
        }
        resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result_json = resp.json()

        print(result_json)

        if not result_json.get('success'):
            raise forms.ValidationError(
                'Wystąpił problem z RECAPTCHA. Spróbuj jeszcze raz... chyba, że jesteś robotem 🤔',
                code='invalid_login')


class InvalidLoginAttemptsCache:
    @staticmethod
    def _key(login):
        return 'invalid_login_attempt_{}'.format(login)

    @staticmethod
    def _value(lockout_timestamp, timebucket):
        return {
            'lockout_start': lockout_timestamp,
            'invalid_attempt_timestamps': timebucket
        }

    @staticmethod
    def delete(login):
        cache.delete(InvalidLoginAttemptsCache._key(login))

    @staticmethod
    def set(login, timebucket, lockout_timestamp=None):
        key = InvalidLoginAttemptsCache._key(login)
        value = InvalidLoginAttemptsCache._value(lockout_timestamp, timebucket)
        cache.set(key, value)

    @staticmethod
    def get(login):
        key = InvalidLoginAttemptsCache._key(login)
        return cache.get(key)
