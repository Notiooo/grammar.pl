from django.views.generic import ListView, TemplateView, FormView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date

from .models import Category, Task_Type, Task, Question, Anwser
from .forms import ContactForm, TaskForm, QuestionForm, QuestionFormSet, AnwserFormSet
from django.db import transaction
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.

class HomePageView(ListView):
    model = Category
    template_name = 'tasks/home.html'


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'tasks/contact.html'
    success_url = 'success'

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(ContactView, self).get_context_data(*args, **kwargs)
        context['age'] = self.give_age(date(1999, 1, 21))
        return context

    def give_age(self, born):
        today = date.today()
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        if (age % 10 in [2, 3, 4]):
            return str(age) + " lata"
        else:
            return str(age) + " lat"


class ContactSuccessView(TemplateView):
    template_name = 'tasks/contact_success.html'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'tasks/category_tasks.html'
    slug_url_kwarg = 'the_slug'
    slug_field = 'slug_url'


def TaskDetailView(request, the_slug, pk):
    # gets the question
    task = Task.objects.get(pk=pk)

    # gets how many anwsers every question has
    number_of_anwsers = len(task.list_of_anwsers())

    # creates a formset with as many fields as the anwsers is
    anwsers_field = modelformset_factory(Anwser, fields=('correct',),
                                         extra=number_of_anwsers)

    if request.method == "POST":
        # gets user anwsers by POST method
        formset = anwsers_field(request.POST)
    else:
        # empty anwsers fields for user
        formset = anwsers_field(queryset=Anwser.objects.none())
    return render(request, 'tasks/task_detail.html',
                  {'formset': formset, 'anwsers': iter(formset), 'task': task, })


class AddTaskListView(LoginRequiredMixin, ListView):
    template_name = 'tasks/add_task_list.html'
    model = Task_Type
    login_url = 'login'
    context_object_name = 'tasks_types'


class AddTaskView(LoginRequiredMixin, CreateView):
    template_name = 'tasks/add_task.html'
    model = Task
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        data = super(AddTaskView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['questions'] = QuestionFormSet(self.request.POST, prefix="questions")
        else:
            data['questions'] = QuestionFormSet(prefix="questions")
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        questions = context['questions']
        with transaction.atomic():
            form.instance.author = self.request.user
            self.object = form.save()
            if questions.is_valid():
                questions.instance = self.object
                questions.save()
        return super(AddTaskView, self).form_valid(form)

    def get_success_url(self):
        if self.request.POST.get('next'):
            if self.request.POST['next'] == 'add_anwsers':
                return reverse_lazy('add_anwsers', kwargs={'pk': self.object.pk})
        return super(AddTaskView, self).get_success_url()


class EditTaskView(LoginRequiredMixin, UpdateView):
    template_name = 'tasks/add_task.html'
    model = Task
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        data = super(EditTaskView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['questions'] = QuestionFormSet(self.request.POST, instance=self.object, prefix="questions")
        else:
            data['questions'] = QuestionFormSet(instance=self.object, prefix="questions")
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        questions = context['questions']
        with transaction.atomic():
            if questions.is_valid():
                questions.save()
        if self.request.POST.get('next') == 'public':
            self.object.public = True
        elif self.request.POST.get('next') == 'unpublic':
            self.object.public = False
        return super(EditTaskView, self).form_valid(form)

    def get_success_url(self):
        if self.request.POST.get('next'):
            if self.request.POST['next'] == 'add_anwser':
                return reverse_lazy('add_anwsers', kwargs={'pk': self.object.id})
            elif self.request.POST['next'] == 'public' or 'unpublic':
                return reverse_lazy('edit_task', kwargs={'pk': self.object.id})
        return super(EditTaskView, self).get_success_url()


class DeleteTaskView(DeleteView):
    template_name = 'tasks/delete_task.html'
    model = Task
    success_url = '/'


class AddTaskAnwsersView(UpdateView):
    template_name = 'tasks/add_anwsers.html'
    model = Task
    fields = []

    def get_context_data(self, **kwargs):
        data = super(AddTaskAnwsersView, self).get_context_data(**kwargs)
        data['anwsers_list'] = []
        questions = self.object.question.all()
        data['anwsers_range'] = range(questions.count())
        if self.request.POST:
            for anwser_number in range(questions.count()):
                data['anwsers_list'].append(
                    AnwserFormSet(self.request.POST, instance=questions[anwser_number],
                                  prefix="anwsers_list{}".format(anwser_number)))
        else:
            for anwser_number in range(questions.count()):
                data['anwsers_list'].append(
                    AnwserFormSet(instance=questions[anwser_number], prefix="anwsers_list{}".format(anwser_number)))
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        anwsers = context['anwsers_list']
        with transaction.atomic():
            for formset in anwsers:
                if formset.is_valid():
                    formset.save()
                else:
                    return super(AddTaskAnwsersView, self).form_invalid(form)
        return super(AddTaskAnwsersView, self).form_valid(form)

    # def get_success_url(self):
    #     return reverse_lazy('add_task', kwargs={'pk': self.object.pk})


class MyTasksView(LoginRequiredMixin, ListView):
    template_name = 'tasks/my_tasks.html'
    context_object_name = 'tasks'
    paginate_by = 15

    def get_queryset(self):
        return Task.objects.filter(author=self.request.user)
