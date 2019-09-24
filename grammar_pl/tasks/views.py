from django.views.generic import ListView, TemplateView, FormView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from django.shortcuts import reverse, get_object_or_404
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template

from datetime import date
from .models import Category, Task_Type, Task, Anwser, Comment, Votes, Favourites
from .forms import ContactForm, TaskCreateForm, TaskUpdateForm, QuestionFormSet, AnwserFormSet, AnwserFormSet_FillGaps, \
    CommentForm, \
    TaskReport_Form
from .helpers import user_vote, user_likes, is_favourite


# ---- CATEGORIES ----

class HomePageView(ListView):
    "The basic home ('/') view, where you can find list of Task Categories"
    model = Category
    template_name = 'tasks/home.html'


class CategoryDetailView(DetailView, MultipleObjectMixin):
    """
    A page with tasks of specific category
    For example: Only tasks for Present Simple
    """
    model = Category
    template_name = 'tasks/category_tasks.html'
    slug_url_kwarg = 'the_slug'
    slug_field = 'slug_url'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # if self.request.GET and 'votes' in self.request.GET:
        #     return super(CategoryDetailView, self).get_context_data(
        #         object_list=sorted(self.get_object().get_public_tasks().order_by('-pk'), key=lambda x: x.get_sum_votes(),
        #                            reverse=True), **kwargs)
        return super(CategoryDetailView, self).get_context_data(
            object_list=self.get_object().get_public_tasks().order_by('-pk'), **kwargs)


# ---- CONTACT -----

class ContactView(FormView):
    "A view with Contact Form, and it contains informations about me (creator of the website)"
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
    "A page displaying when the Contact Form from ContactView was filled in correctly"
    template_name = 'tasks/contact_success.html'


# ------- TASK VIEWS --------

class PublicTasksView(ListView):
    """
    A page with all public tasks
    """
    model = Task
    template_name = 'tasks/tasks_list.html'
    paginate_by = 10

    def get_queryset(self):
        return self.model.objects.filter(public=True).order_by('-pk')


class TaskDetailView(DetailView, MultipleObjectMixin):
    """
    A page where you can actually see other user Task.
    You can anwser to questions, check result.
    You can post comment, upvote/downvote Task, or Like other people comments

    number_of_anwsers -> Used to generate right amount of empty fields to fill in
    anwsers_field     -> The actual fields user can fill in with his anwsers
    object_list       -> Object used to paginate. In this example it is list of comments
    user_vote         -> It checks if user has upvote/downvote this task before.
                         It is used to properly display (color) user vote.
    user_likes        -> It's a list with ID's of comments user gave a LIKE before.
                         It is used to properly display what comment user has liked before.
    comment_form      -> A form user can fill in to post a comment
    formset           -> A formset made of anwsers_field user can fill in and get score/results/anwsers.
    anwsers           -> An iter of formset. Used for single iteration, with no repeat. One call -> one anwser
    """

    model = Task
    context_object_name = 'task'
    paginate_by = 10

    def get_template_names(self):
        return 'tasks/layouts/task_detail_{}.html'.format(self.get_object().task_type.layout_name)

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        number_of_anwsers = len(obj.list_of_anwsers())
        anwsers_field = modelformset_factory(Anwser, fields=('correct', 'text'),
                                             extra=number_of_anwsers)
        comments_list = obj.comments.all().order_by('-id')
        formset = anwsers_field(queryset=Anwser.objects.none())

        return super(TaskDetailView, self).get_context_data(number_of_anwsers=number_of_anwsers,
                                                            anwsers_field=anwsers_field,
                                                            object_list=comments_list,
                                                            user_vote=user_vote(self.request, obj),
                                                            user_likes=user_likes(self.request, obj),
                                                            is_favourite=is_favourite(self.request, obj),
                                                            comment_form=CommentForm(),
                                                            formset=formset,
                                                            user_anwsers=iter(formset), **kwargs)

    def post(self, request, **kwargs):
        user = request.user
        self.object = self.get_object()

        # if user wants to add an comment (comment form submitted)
        if 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.author = user
                comment.task = self.object
                comment.save()
                return HttpResponseRedirect("#comments")
            else:
                context = self.get_context_data(**kwargs)
                context['comment_form'] = comment_form
                return self.render_to_response(context)

        context = self.get_context_data(**kwargs)
        context['formset'] = context['anwsers_field'](request.POST)
        context['user_anwsers'] = iter(context['formset'])
        return self.render_to_response(context)


class EditTaskView(LoginRequiredMixin, UpdateView):
    "A page where user can edit his own task"

    template_name = 'tasks/actions/add_task.html'
    login_url = 'login'
    model = Task
    form_class = TaskUpdateForm

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            raise Http404("Wybacz, ale to niedozwolone. To nie twoje dzieło!")
        return super(EditTaskView, self).dispatch(request, *args, **kwargs)

    # def get_template_names(self):
    #     return 'tasks/actions/layouts/add_task_{}.html'.format(self.get_object().task_type.layout_name)

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


class MyTasksView(LoginRequiredMixin, ListView):
    "A page where user can see tasks he made"

    template_name = 'tasks/my_tasks.html'
    context_object_name = 'tasks'
    paginate_by = 15
    login_url = 'login'

    def get_queryset(self):
        return Task.objects.filter(author=self.request.user).order_by('-pk')


class MyFavouritesView(LoginRequiredMixin, ListView):
    "A page where user can see his favourite tasks"
    template_name = 'tasks/my_favourites.html'
    context_object_name = 'tasks'
    paginate_by = 15
    login_url = 'login'

    def get_queryset(self):
        favourites = Favourites.objects.filter(user=self.request.user).order_by('-pk')
        return [favourite.task for favourite in favourites]


class DeleteTaskView(LoginRequiredMixin, DeleteView):
    "A page where user can confirm deleting his own task"

    template_name = 'tasks/actions/delete_task.html'
    model = Task
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            raise Http404("Wybacz, ale to niedozwolone. To nie twoje dzieło!")
        return super(DeleteTaskView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('my_tasks')


def task_random(request):
    "This view returns a random task from a given exam_category"

    random = Task.objects.order_by('?').first()
    if random:
        return HttpResponseRedirect(
            reverse('task_detail', kwargs={'pk': random.pk, 'the_slug': random.category.slug_url}))
    else:
        raise Http404('Przepraszamy, w tej chwili nie ma żadnych zadań')


# ------- ADD TASKS VIEWS -------

class AddTaskListView(LoginRequiredMixin, ListView):
    """
    A page where user can choose his Type of Task he want to create.
    For example:
    - ABC Quiz
    - Fill empty fields
    """

    template_name = 'tasks/actions/add_task_list.html'
    model = Task_Type
    login_url = 'login'
    context_object_name = 'tasks_types'


class AddTaskView(LoginRequiredMixin, CreateView):
    "A page where user can create his own task"

    login_url = 'login'
    model = Task
    form_class = TaskCreateForm

    def get_template_names(self):
        try:
            return get_template('tasks/actions/layouts/add_task_{}.html'.format(
                get_object_or_404(Task_Type, slug_url=self.kwargs['task_name']).layout_name))
        except TemplateDoesNotExist:
            return 'tasks/actions/add_task.html'

    def get_context_data(self, **kwargs):
        data = super(AddTaskView, self).get_context_data(**kwargs)
        print(self.request)
        data['task_type'] = get_object_or_404(Task_Type, slug_url=self.kwargs['task_name'])
        if self.request.POST:
            data['questions'] = QuestionFormSet(self.request.POST, prefix="questions")
        else:
            data['questions'] = QuestionFormSet(prefix="questions")
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        questions = context['questions']
        print(form)
        if get_object_or_404(Task_Type, slug_url=self.kwargs['task_name']).layout_name == 'fill-gap':
            for question in questions:
                if (question['text'].value().count('_') != 1):
                    form.add_error(None, 'Jedno z twoich pytań nie zawiera luk')
                    return super(AddTaskView, self).form_invalid(form)
        with transaction.atomic():
            form.instance.author = self.request.user
            form.instance.task_type = context['task_type']
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


class AddTaskAnwsersView(LoginRequiredMixin, UpdateView):
    "A page where user can add anwsers to questions he created in AddTaskView"

    template_name = 'tasks/actions/add_anwsers.html'
    login_url = 'login'
    model = Task
    fields = []

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            raise Http404("Wybacz, ale to niedozwolone. To nie twoje dzieło!")
        return super(AddTaskAnwsersView, self).dispatch(request, *args, **kwargs)

    # def get_template_names(self):
    #     return 'tasks/actions/layouts/add_anwsers_{}.html'.format(self.get_object().task_type.layout_name)

    def get_context_data(self, **kwargs):
        formsets = {'fill-gap': AnwserFormSet_FillGaps,
                    'quiz': AnwserFormSet}
        CreateForm = formsets.get(self.get_object().task_type.layout_name)

        data = super(AddTaskAnwsersView, self).get_context_data(**kwargs)
        data['anwsers_list'] = []
        questions = self.object.question.all()
        data['anwsers_range'] = range(questions.count())
        if self.request.POST:
            for anwser_number in range(questions.count()):
                data['anwsers_list'].append(
                    CreateForm(self.request.POST, instance=questions[anwser_number],
                               prefix="anwsers_list{}".format(anwser_number)))
        else:
            for anwser_number in range(questions.count()):
                data['anwsers_list'].append(
                    CreateForm(instance=questions[anwser_number], prefix="anwsers_list{}".format(anwser_number)))
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


# -------- COMMENT VIEWS ----------

class DeleteCommentView(LoginRequiredMixin, DeleteView):
    "A page where user can fonfirm deleting his own comment"

    template_name = 'tasks/actions/delete_comment.html'
    login_url = 'login'
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
            return reverse('task_detail', kwargs={'pk': task_id, 'the_slug': the_slug}) + "#comments"
        else:
            return reverse('home')


# ------- REPORT VIEWS ---------

class TaskReport(FormView):
    "It allows users to report (send email) describing a problem with a task"

    form_class = TaskReport_Form
    template_name = 'report/report.html'

    def get_context_data(self, *args, **kwargs):
        context = super(TaskReport, self).get_context_data(*args, **kwargs)
        context['obj'] = get_object_or_404(Task, pk=self.kwargs['task_id'])
        return context

    def form_valid(self, form):
        form.send_email(self.kwargs['task_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return 'success' + "?next={}".format(self.request.GET['next'])


class TaskReportSuccess(TemplateView):
    "Simple view showing a success page if the Report form passed"
    template_name = 'report/report_success.html'


# ------- AJAX VIEWS ----------

def add_like(request, pk):
    "A page for Ajax made for giving likes to users comments"

    if request.user.is_authenticated:
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
    else:
        raise Http404('test')


def add_vote(request, pk, vote_type):
    "A page for Ajax made for giving votes (upvote/downvote) to users tasks"

    if request.user.is_authenticated:
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
    else:
        raise Http404


def add_favourite(request, pk):
    "A page for Ajax adding Task to user favourite list"

    if request.user.is_authenticated:
        object = Task.objects.get(id=pk)
        try:
            object.favourites.create(task=object, user=request.user)
            favourite = True
        except IntegrityError:
            object.favourites.get(task=object, user=request.user).delete()
            favourite = False
        return JsonResponse(dict(is_favourite=favourite))
    else:
        raise Http404
