from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.AttendanceListView.as_view(), name='attendance_list'),
    path('create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('<int:pk>/update/', views.AttendanceUpdateView.as_view(), name='attendance_update'),
    path('<int:pk>/delete/', views.AttendanceDeleteView.as_view(), name='attendance_delete'),
    path('calendar/', views.attendance_calendar_view, name='attendance_calendar'),
    path('api/employee/<int:employee_id>/', views.get_employee_attendance, name='api_employee_attendance'),
    path('bulk-create/', views.bulk_attendance_create, name='bulk_attendance_create'),
]
