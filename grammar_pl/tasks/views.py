from django.views.generic import ListView, TemplateView, FormView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date

from .models import Category, Task_Type, Task, Anwser, Comment, Votes
from .forms import ContactForm, TaskForm, QuestionForm, QuestionFormSet, AnwserFormSet, CommentForm
from django.db import transaction
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404, reverse
from .helpers import save_user_vote, user_vote, user_likes
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseRedirect
from django.views.generic.list import MultipleObjectMixin


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


class TaskDetailView(DetailView, MultipleObjectMixin):
    template_name = 'tasks/task_detail.html'
    model = Task
    context_object_name = 'task'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        number_of_anwsers = len(obj.list_of_anwsers())
        anwsers_field = modelformset_factory(Anwser, fields=('correct',),
                                             extra=number_of_anwsers)
        comments_list = obj.comments.all().order_by('-id')
        formset = anwsers_field(queryset=Anwser.objects.none())

        return super(TaskDetailView, self).get_context_data(number_of_anwsers=number_of_anwsers,
                                                            anwsers_field=anwsers_field,
                                                            object_list=comments_list,
                                                            user_vote=user_vote(self.request, obj),
                                                            user_likes=user_likes(self.request, obj),
                                                            comment_form=CommentForm(),
                                                            formset=formset,
                                                            anwsers=iter(formset), **kwargs)

    def post(self, request, **kwargs):
        user = request.user
        self.object = self.get_object()
        if 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.author = user
                comment.task = self.object
                comment.save()
            return HttpResponseRedirect("#comments")
        context = self.get_context_data(**kwargs)
        context['formset'] = context['anwsers_field'](request.POST)
        context['anwsers'] = iter(context['formset'])
        return self.render_to_response(context)


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
                return reverse('add_anwsers', kwargs={'pk': self.object.id})
            elif self.request.POST['next'] == 'public' or 'unpublic':
                return reverse('edit_task', kwargs={'pk': self.object.id})
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


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    template_name = 'tasks/delete_comment.html'
    model = Comment

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            raise Http404("Wybacz, ale to niedozwolone. To nie twoje dzieło!")
        return super(DeleteCommentView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        task_id = self.request.POST.get('task-id')
        the_slug = self.request.POST.get('the_slug')
        if task_id and the_slug:
            return reverse('task_detail', kwargs={'pk': task_id, 'the_slug': the_slug})
        else:
            return reverse('home')


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


# ------- AJAX VIEWS ----------
from django.http import JsonResponse

def add_like(request, pk):
    liked = False
    try:
        Comment.objects.get(id=pk).likes.create(user=request.user)
        liked = True
    except IntegrityError:
        Comment.objects.get(id=pk).likes.get(user=request.user).delete()
    except ObjectDoesNotExist:
        pass
    data = {
        'liked': liked,
        'count': Comment.objects.get(id=pk).likes.count()
    }
    return JsonResponse(data)

def add_vote(request, pk, vote_type):
    object = Task.objects.get(id=pk)
    if vote_type == 'upvote':
        try:
            object.votes.create(activity_type=Votes.UP_VOTE, user=request.user)
        except IntegrityError:
            obj = object.votes.get(user=request.user)
            obj.activity_type = Votes.UP_VOTE
            obj.save()
    else:
        try:
            object.votes.create(activity_type=Votes.DOWN_VOTE, user=request.user)
        except IntegrityError:
            obj = object.votes.get(user=request.user)
            obj.activity_type = Votes.DOWN_VOTE
            obj.save()
    data = {
        'upvotes': object.votes.filter(activity_type=Votes.UP_VOTE).count(),
        'downvotes': object.votes.filter(activity_type=Votes.DOWN_VOTE).count(),
    }
    return JsonResponse(data)