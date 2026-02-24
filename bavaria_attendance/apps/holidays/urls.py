from django.urls import path
from . import views

app_name = 'holidays'

urlpatterns = [
    path('', views.HolidayListView.as_view(), name='holiday_list'),
    path('create/', views.HolidayCreateView.as_view(), name='holiday_create'),
    path('<int:pk>/update/', views.HolidayUpdateView.as_view(), name='holiday_update'),
    path('<int:pk>/delete/', views.HolidayDeleteView.as_view(), name='holiday_delete'),
    path('calendar/', views.holiday_calendar_view, name='holiday_calendar'),
]
