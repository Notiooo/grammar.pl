from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, FormView, TemplateView
from django.urls.base import reverse
from django.http import HttpResponseRedirect

from django.forms import modelformset_factory

from . import models, forms


class MaturaHomepage(ListView):
    model = models.Matura_Task
    template_name = 'matura/matura_home.html'

    def get_queryset(self):
        queryset = models.Matura_Task.objects.values('year', 'level').distinct()
        MaturaHomepage.append_verbal(self, queryset)
        return {'queryset': queryset,
                'types': models.Matura_Task.types}

    def get_types(self):
        types = [obj[1] for obj in models.Matura_Task.types]
        return types

    def append_verbal(self, queryset):
        LEVELS = models.Matura_Task.LEVELS
        for column in queryset:
            for tup in LEVELS:
                if column['level'] == tup[0]:
                    column['level_verbal'] = tup[1]


class MaturaCategory(ListView):
    model = models.Matura_Task
    template_name = 'matura/matura_list.html'
    paginate_by = 10

    def get_queryset(self):
        return models.Matura_Task.objects.filter(type=self.kwargs['type'])


class MaturaLevel(ListView):
    model = models.Matura_Task
    template_name = 'matura/matura_list.html'
    paginate_by = 10

    def get_queryset(self):
        return models.Matura_Task.objects.filter(year=self.kwargs['year'], level=self.kwargs['level'])


def MaturaDetail(request, year, pk):
    # gets the question
    task = models.Matura_Task.objects.get(pk=pk)

    # gets how many anwsers every question has
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
    return render(request, 'matura/matura_detail_{0}.html'.format(task.layout),
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
    return HttpResponseRedirect(reverse('matura_detail', kwargs={'pk': random.pk, 'year': random.year}))
