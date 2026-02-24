"""
URL configuration for Bavaria Attendance project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('employees/', include('apps.employees.urls', namespace='employees')),
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),
    path('leave/', include('apps.leave_management.urls', namespace='leave')),
    path('holidays/', include('apps.holidays.urls', namespace='holidays')),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False), name='home'),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
