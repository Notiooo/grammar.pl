from django.shortcuts import render
from django.views import generic
from django.views.generic import ListView, TemplateView

from .models import Category, Question

# Create your views here.

class HomePageView(ListView):
    model = Category
    template_name = 'tasks/home.html'

class ContactView(TemplateView):
    template_name = 'tasks/contact.html'

class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = 'tasks/category.html'
    slug_url_kwarg = 'the_slug'

class QuestionDetailView(generic.DetailView):
    model = Question
    template_name = 'tasks/question.html'