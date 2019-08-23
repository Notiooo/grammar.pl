from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('<slug:the_slug>/', views.CategoryDetailView.as_view(), name='category'),
    path('<slug:the_slug>/<int:pk>/', views.QuestionDetailView.as_view(), name='question'),
]
