from django.views.generic import ListView, TemplateView, FormView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date

from .models import Category, Task_Type, Task, Anwser
from .forms import ContactForm, TaskForm, QuestionForm, QuestionFormSet, AnwserFormSet, CommentForm
from django.db import transaction
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404
from .helpers import save_user_vote, user_vote, user_likes
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.http import Http404


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
    task = get_object_or_404(Task, pk=pk)

    # gets how many anwsers every question has
    number_of_anwsers = len(task.list_of_anwsers())

    # creates a formset with as many fields as the anwsers is
    anwsers_field = modelformset_factory(Anwser, fields=('correct',),
                                         extra=number_of_anwsers)

    if request.method == 'POST' and 'add_comment' in request.POST:
        formset = anwsers_field(queryset=Anwser.objects.none())
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.task = task
            comment.save()
    elif request.method == 'POST' and 'like' in request.POST:
        formset = anwsers_field(queryset=Anwser.objects.none())
        comment_form = CommentForm(request.POST)
        try:
            task.comments.get(id=request.POST['like']).likes.create(user=request.user)
        except IntegrityError:
            task.comments.get(id=request.POST['like']).likes.get(user=request.user).delete()
        except ObjectDoesNotExist:
            pass
    elif request.method == "POST":
        save_user_vote(request, task)
        comment_form = CommentForm()
        formset = anwsers_field(request.POST)
    else:
        # empty anwsers fields for user
        comment_form = CommentForm()
        formset = anwsers_field(queryset=Anwser.objects.none())

    # paginator-----
    comments_list = task.comments.all().order_by('-id')
    paginator = Paginator(comments_list, 10)
    page = request.GET.get('page')
    comments = paginator.get_page(page)
    return render(request, 'tasks/task_detail.html',
                  {'formset': formset, 'anwsers': iter(formset), 'task': task,
                   'user_vote': user_vote(request, task), 'user_likes': user_likes(request, task),
                   'comment_form': comment_form, 'comments': comments})


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

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            raise Http404("Wybacz, ale to niedozwolone. To nie twoje dzieło!")
        return super(EditTaskView, self).dispatch(request, *args, **kwargs)

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


class DeleteTaskView(LoginRequiredMixin, DeleteView):
    template_name = 'tasks/delete_task.html'
    model = Task
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            raise Http404("Wybacz, ale to niedozwolone. To nie twoje dzieło!")
        return super(DeleteTaskView, self).dispatch(request, *args, **kwargs)


class AddTaskAnwsersView(LoginRequiredMixin, UpdateView):
    template_name = 'tasks/add_anwsers.html'
    model = Task
    fields = []

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            raise Http404("Wybacz, ale to niedozwolone. To nie twoje dzieło!")
        return super(AddTaskAnwsersView, self).dispatch(request, *args, **kwargs)

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
        return Task.objects.filter(author=self.request.user).order_by('-pk')
