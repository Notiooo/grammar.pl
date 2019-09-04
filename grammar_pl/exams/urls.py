from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExamsHomepage.as_view(), name='exams_home'),
    path('random/<slug:exam_category>', views.exams_random, name='exams_random'),
    path('report/<int:task_id>', views.ExamsReport.as_view(), name='exams_report'),
    path('report/success', views.ExamsReportSuccess.as_view(), name='exams_report_success'),
    path('search/', views.Exams_Search.as_view(), name='exams_search'),
    path('<slug:exam_category>', views.ExamsCategory.as_view(), name='exams_category'),
    path('<slug:exam_category>/<slug:task_type>/', views.ExamsByTaskType.as_view(), name='exams_by_task_type'),
    path('<slug:exam_category>/<slug:exam_slug_url>', views.ExamsLevel.as_view(), name='exams_level'),
    path('<slug:exam_category>/<int:year>/<int:pk>', views.ExamsDetail, name='exams_detail'),
]
