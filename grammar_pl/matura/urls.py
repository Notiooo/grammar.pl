from django.urls import path
from . import views

urlpatterns = [
    path('', views.MaturaHomepage.as_view(), name='matura_home'),
    path('<int:year>/<int:pk>', views.MaturaDetail, name='matura_detail'),
    path('<slug:slug_url>', views.MaturaLevel.as_view(), name='matura_level'),
    path('<slug:type>/', views.MaturaType.as_view(), name='matura_type'),
    path('report/<int:task_id>', views.MaturaReport.as_view(), name='matura_report'),
    path('report/success', views.MaturaReportSuccess.as_view(), name='matura_success'),
    path('random', views.matura_random, name='matura_random'),
]
