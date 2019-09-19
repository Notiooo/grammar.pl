from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('<int:pk>/', views.ProfileDetailView.as_view(), name='profile'),
    path('<int:pk>/comments/', views.ProfileCommentsActivity.as_view(), name='profile_comments'),
    path('<int:pk>/tasks/', views.ProfileTasksActivity.as_view(), name='profile_tasks'),
    path('change/', views.ChangeProfileView.as_view(), name='changeprofile'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
]
