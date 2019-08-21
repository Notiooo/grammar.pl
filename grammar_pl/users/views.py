from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'


class ChangeProfileView(LoginRequiredMixin, generic.UpdateView):
    form_class = CustomUserChangeForm
    template_name = 'users/changeprofile.html'
    login_url = 'login'

    def get_object(self):
        return self.request.user

class ProfileDetailView(generic.DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
