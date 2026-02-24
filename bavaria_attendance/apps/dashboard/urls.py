from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('api/', views.dashboard_api, name='dashboard_api'),
    path('salary-report/', views.SalaryReportView.as_view(), name='salary_report'),
]
