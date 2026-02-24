from django.urls import path
from . import views

app_name = 'leave_management'

urlpatterns = [
    path('', views.LeaveListView.as_view(), name='leave_list'),
    path('create/', views.LeaveCreateView.as_view(), name='leave_create'),
    path('<int:pk>/update/', views.LeaveUpdateView.as_view(), name='leave_update'),
    path('<int:pk>/delete/', views.LeaveDeleteView.as_view(), name='leave_delete'),
    path('<int:pk>/approve/', views.approve_leave, name='leave_approve'),
    path('<int:pk>/reject/', views.reject_leave, name='leave_reject'),
]
