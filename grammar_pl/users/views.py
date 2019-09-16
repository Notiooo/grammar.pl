from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm
from .models import CustomUser
from tasks.models import Task, Activity

from django.contrib.auth import views as auth_views


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


class CustomLoginView(auth_views.LoginView):
    authentication_form = CustomAuthenticationForm


class ProfileDetailView(generic.DetailView):
    model = CustomUser
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        user = self.get_object()
        context['tasks_activity'] = Task.objects.filter(author=user).order_by('-id')[:3]
        user_activity = Activity.objects.filter(user=user)
        context['gained_points'] = user_activity.filter(activity_type=Activity.UP_VOTE).count() - user_activity.filter(activity_type=Activity.DOWN_VOTE).count()
        return context