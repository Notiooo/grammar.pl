from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.views.generic import ListView, FormView, TemplateView, DetailView
from django.urls.base import reverse
from django.http import HttpResponseRedirect
from django.views.generic.list import MultipleObjectMixin

from django.forms import modelformset_factory

from . import models, forms


class ExamsHomepage(TemplateView):
    """
    A homepage where you can choose what type of exam you want to browse
    It should return an 'exams_types' in context with all categories that are available in Exams_Category model
    """

    template_name = 'exams/exams_home.html'

    def get_context_data(self, **kwargs):
        """
        It collects all exam categories like:
        - Matura
        - Egzamin Ośmioklasisty
        - Egzamin Gimnazjalny
        """

        exams_types = models.Exams_Category.get_category_types()
        context = super(ExamsHomepage, self).get_context_data(exams_types=exams_types, **kwargs)
        return context


class ExamsCategory(ListView):
    """
    It allows you to browse a tasks of specific category
    It should return a context with:
    'task_types' - a list of task types from Exams_Task model
    """

    model = models.Exams_Category
    template_name = 'exams/exams_category_home.html'
    paginate_by = 10
    ordering = '-year'

    def get_context_data(self, **kwargs):
        "It gets a list of task types"

        task_types = self.model.get_task_types()
        context = super(ExamsCategory, self).get_context_data(task_types=task_types, **kwargs)
        return context

    def get_queryset(self):
        "If this exam category has any exercise/task then it's a correct one"

        return get_list_or_404(self.model.objects.filter(type=self.kwargs['exam_category']).order_by('pk'))


class ExamsByTaskType(ListView):
    """
    A list showing only a specific task type of specific exam category
    Like for example: /exams/matura/audio/ - shows only listening tasks of matura (specific Exam_Task type)
    """

    model = models.Exams_Task
    template_name = 'exams/exams_list.html'
    context_object_name = 'tasks'
    paginate_by = 15

    def get_queryset(self):
        return self.model.objects.filter(type=self.kwargs['task_type'],
                                         category__type=self.kwargs['exam_category']).order_by('pk')


class ExamsLevel(DetailView, MultipleObjectMixin):
    """
    A list of specific exam_category tasks
    Example: /exams/matura/2019-pod-maj/
    """

    model = models.Exams_Category
    template_name = 'exams/exams_list.html'
    slug_url_kwarg = 'exam_slug_url'
    slug_field = 'slug_url'
    context_object_name = 'category'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        object_list = self.object.task.all().order_by('pk')
        context = super(ExamsLevel, self).get_context_data(object_list=object_list, **kwargs)
        # context['tasks'] = context['object'].task.all()
        return context


def ExamsDetail(request, exam_category, year, pk):
    # gets the question
    task = models.Exams_Task.objects.get(pk=pk)

    # gets how many anwsers every question has
    if task.layout == "fill-gap":  # fillgaps anwsers are equal to number of questions
        number_of_anwsers = task.question.all().count()
    else:
        number_of_anwsers = len(task.list_of_anwsers())

    # creates a formset with as many fields as the anwsers is
    anwsers_field = modelformset_factory(models.Exams_Anwser, fields=('correct_anwser', 'text',),
                                         extra=number_of_anwsers)

    if request.method == "POST":
        # gets user anwsers by POST method
        formset = anwsers_field(request.POST)
    else:
        # empty anwsers fields for user
        formset = anwsers_field(queryset=models.Exams_Anwser.objects.none())
    return render(request, 'exams/layouts/exams_detail_{0}.html'.format(task.layout),
                  {'formset': formset, 'anwsers': iter(formset), 'task': task, 'opts': models.Exams_Task._meta, })


class ExamsReport(FormView):
    "It allows users to report (send email) describing a problem with a task"

    form_class = forms.ExamsReport_Form
    template_name = 'exams/exams_report.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ExamsReport, self).get_context_data(*args, **kwargs)
        context['obj'] = get_object_or_404(models.Exams_Task, pk=self.kwargs['task_id'])
        return context

    def form_valid(self, form):
        form.send_email(self.kwargs['task_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return 'success' + "?next={}".format(self.request.GET['next'])


class ExamsReportSuccess(TemplateView):
    template_name = 'exams/exams_report_success.html'


def exams_random(request, exam_category):
    random = models.Exams_Task.objects.filter(category__type=exam_category).order_by('?').first()
    return HttpResponseRedirect(reverse('exams_detail', kwargs={'pk': random.pk, 'year': random.get_year(), 'exam_category': exam_category}))


class Exams_Search(ListView):
    template_name = 'exams/exams_search.html'
    model = models.Exams_Task
    context_object_name = 'tasks'
    paginate_by = 15

    def get_queryset(self):
        return models.Exams_Task.objects.filter(title__contains=self.request.GET.get('search'))
