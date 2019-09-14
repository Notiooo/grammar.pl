from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('contact/success', views.ContactSuccessView.as_view(), name='contact_success'),
    path('add_task/', views.AddTaskListView.as_view(), name='add_task_list'),
    path('add_task/<slug:task_name>', views.AddTaskView.as_view(), name='add_task'),
    path('edit_task/<int:pk>', views.EditTaskView.as_view(), name='edit_task'),
    path('delete_task/<int:pk>', views.DeleteTaskView.as_view(), name='delete_task'),
    path('add_anwsers/<int:pk>', views.AddTaskAnwsersView.as_view(), name='add_anwsers'),
    path('<slug:the_slug>/', views.CategoryDetailView.as_view(), name='category'),
]
