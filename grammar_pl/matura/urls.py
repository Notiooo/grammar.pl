from django.urls import path
from . import views

urlpatterns = [
    path('', views.MaturaHomepage.as_view(), name='matura_home'),
    path('<int:year>/<int:pk>', views.MaturaDetail, name='matura_detail'),
    path('<int:year>/<slug:level>', views.MaturaLevel.as_view(), name='matura_level'),
    path('<slug:type>/', views.MaturaCategory.as_view(), name='matura_category'),
    path('random', views.matura_random, name='matura_random'),
]