from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm
from .models import CustomUser

from django.contrib.auth import views as auth_views

from tasks.models import Task, Votes, Likes, Comment


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

    @staticmethod
    def get_user_gained_points(user):
        gained_points = 0
        for task in Task.objects.filter(author=user):
            gained_points += task.get_sum_votes()
        return gained_points

    @staticmethod
    def get_user_gained_likes(user):
        gained_likes = 0
        for comment in Comment.objects.filter(author=user):
            gained_likes += comment.likes.count()
        return gained_likes

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        user = self.get_object()
        context['tasks_activity'] = Task.objects.filter(author=user).order_by('-id')[:3]
        context['comments_activity'] = Comment.objects.filter(author=user).order_by('-id')[:3]
        context['gained_points'] = self.get_user_gained_points(user)
        context['gained_likes'] = self.get_user_gained_likes(user)
        return context
