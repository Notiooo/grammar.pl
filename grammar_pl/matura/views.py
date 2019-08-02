from django.shortcuts import render
from django.views.generic import ListView, DetailView
from . import models


# Create your views here.

class MaturaHomepage(ListView):
    model = models.Matura_Task
    template_name = 'matura/matura_home.html'

    def get_queryset(self):
        return {'queryset': models.Matura_Task.objects.values_list('year', 'level').distinct(),
                'types': models.Matura_Task.types}

    def get_types(self):
        types = [obj[1] for obj in models.Matura_Task.types]
        return types


class MaturaYear(ListView):
    model = models.Matura_Task
    template_name = 'matura/matura_list.html'

    def get_queryset(self):
        return models.Matura_Task.objects.filter(year=self.kwargs['year'])


class MaturaDetail(DetailView):
    model = models.Matura_Task
    template_name = 'matura/matura_detail.html'


class MaturaCategory(ListView):
    model = models.Matura_Task
    template_name = 'matura/matura_list.html'

    def get_queryset(self):
        return models.Matura_Task.objects.filter(type=self.kwargs['type'])


class MaturaLevel(ListView):
    model = models.Matura_Task
    template_name = 'matura/matura_list.html'

    def get_queryset(self):
        return models.Matura_Task.objects.filter(year=self.kwargs['year'])
