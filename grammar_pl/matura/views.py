from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, FormView, TemplateView, DetailView
from django.urls.base import reverse
from django.http import HttpResponseRedirect
from django.views.generic.list import MultipleObjectMixin

from django.forms import modelformset_factory

from . import models, forms


class MaturaHomepage(ListView):
    model = models.Matura_Category
    template_name = 'matura/matura_home.html'
    paginate_by = 10
    ordering = '-year'

    def get_context_data(self, **kwargs):
        types = self.model.get_types()
        context = super(MaturaHomepage, self).get_context_data(types=types, **kwargs)
        return context


class MaturaType(ListView):
    model = models.Matura_Task
    template_name = 'matura/matura_list.html'
    context_object_name = 'tasks'
    paginate_by = 15

    def get_queryset(self):
        return self.model.objects.filter(type=self.kwargs['type']).order_by('pk')


class MaturaLevel(DetailView, MultipleObjectMixin):
    model = models.Matura_Category
    template_name = 'matura/matura_list.html'
    slug_url_kwarg = 'slug_url'
    slug_field = 'slug_url'
    context_object_name = 'category'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        object_list = self.object.task.all().order_by('pk')
        context = super(MaturaLevel, self).get_context_data(object_list=object_list, **kwargs)
        # context['tasks'] = context['object'].task.all()
        return context


def MaturaDetail(request, year, pk):
    # gets the question
    task = models.Matura_Task.objects.get(pk=pk)

    # gets how many anwsers every question has
    if task.layout == "fill-gap":  # fillgaps anwsers are equal to number of questions
        number_of_anwsers = task.question.all().count()
    else:
        number_of_anwsers = len(task.list_of_anwsers())

    # creates a formset with as many fields as the anwsers is
    anwsers_field = modelformset_factory(models.Matura_Anwser, fields=('correct_anwser', 'text',),
                                         extra=number_of_anwsers)

    if request.method == "POST":
        # gets user anwsers by POST method
        formset = anwsers_field(request.POST)
    else:
        # empty anwsers fields for user
        formset = anwsers_field(queryset=models.Matura_Anwser.objects.none())
    return render(request, 'matura/layouts/matura_detail_{0}.html'.format(task.layout),
                  {'formset': formset, 'anwsers': iter(formset), 'task': task, 'opts': models.Matura_Task._meta, })


class MaturaReport(FormView):
    form_class = forms.MaturaReport_Form
    template_name = 'matura/matura_report.html'

    def get_context_data(self, *args, **kwargs):
        context = super(MaturaReport, self).get_context_data(*args, **kwargs)
        context['obj'] = get_object_or_404(models.Matura_Task, pk=self.kwargs['task_id'])
        return context

    # def get_context_data(self, *args, **kwargs):
    #     get_object_or_404(models.Matura_Task, pk=self.kwargs['task_id'])
    #     return super(MaturaReport, self).get_context_data(*args, **kwargs)

    def form_valid(self, form):
        form.send_email(self.kwargs['task_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return 'success' + "?next={}".format(self.request.GET['next'])


class MaturaReportSuccess(TemplateView):
    template_name = 'matura/matura_report_success.html'


def matura_random(request):
    random = models.Matura_Task.objects.order_by('?').first()
    return HttpResponseRedirect(reverse('matura_detail', kwargs={'pk': random.pk, 'year': random.get_year()}))
