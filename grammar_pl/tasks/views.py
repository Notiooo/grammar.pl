from django.shortcuts import render
from django.views import generic
from django.views.generic import ListView, TemplateView
from datetime import date

from .models import Category, Question


# Create your views here.

class HomePageView(ListView):
    model = Category
    template_name = 'tasks/home.html'


class ContactView(TemplateView):
    template_name = 'tasks/contact.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ContactView, self).get_context_data(*args, **kwargs)
        context['age'] = self.give_age(date(1999, 1, 21))
        return context

    def give_age(self, born):
        today = date.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        if(age%10 in [2,3,4]):
            return str(age) + " lata"
        else:
            return str(age) + " lat"


class CategoryDetailView(generic.DetailView):
    model = Category
    template_name = 'tasks/category.html'
    slug_url_kwarg = 'the_slug'


class QuestionDetailView(generic.DetailView):
    model = Question
    template_name = 'tasks/question.html'
