from django.urls import path
from . import views

urlpatterns = [
    #homepage
    path('', views.HomePageView.as_view(), name='home'),

    #contact
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('contact/success', views.ContactSuccessView.as_view(), name='contact_success'),

    #tasks
    path('add_task/', views.AddTaskListView.as_view(), name='add_task_list'),
    path('add_task/<slug:task_name>', views.AddTaskView.as_view(), name='add_task'),
    path('edit_task/<int:pk>', views.EditTaskView.as_view(), name='edit_task'),
    path('delete_task/<int:pk>', views.DeleteTaskView.as_view(), name='delete_task'),
    path('my_tasks/', views.MyTasksView.as_view(), name='my_tasks'),
    path('my_favourites/', views.MyFavouritesView.as_view(), name='my_favourites'),
    path('add_anwsers/<int:pk>', views.AddTaskAnwsersView.as_view(), name='add_anwsers'),
    path('random/', views.task_random, name='task_random'),

    #report
    path('report/<int:task_id>', views.TaskReport.as_view(), name='task_report'),
    path('report/success', views.TaskReportSuccess.as_view(), name='task_report_success'),

    #comments
    path('comment/delete/<int:pk>', views.DeleteCommentView.as_view(), name='delete_comment'),

    #ajax actions
    path('comment/like/<int:pk>', views.add_like, name="add_like"),
    path('task/add_favourite/<int:pk>/', views.add_favourite, name='add_favourite'),
    path('task/vote/<int:pk>/<slug:vote_type>/', views.add_vote, name="add_vote"),

    #categories
    path('<slug:the_slug>/', views.CategoryDetailView.as_view(), name='category'),
    path('<slug:the_slug>/<int:pk>', views.TaskDetailView.as_view(), name='task_detail'),

    #sitemap
    path('sitemap.xml', views.sitemap, name="sitemap"),
]
