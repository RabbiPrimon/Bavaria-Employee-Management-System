from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta, date as date_obj
from calendar import monthrange
import calendar
from .models import Attendance
from .forms import AttendanceForm, AttendanceFilterForm, BulkAttendanceForm
from apps.employees.models import Employee


class AttendanceMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to check if user is admin or HR.
    """
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_hr


class AttendanceListView(LoginRequiredMixin, ListView):
    """
    List all attendance records with filtering.
    """
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Attendance.objects.select_related('employee').all()
        
        # Apply filters
        employee = self.request.GET.get('employee')
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        status = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if employee:
            queryset = queryset.filter(employee_id=employee)
        
        if month:
            queryset = queryset.filter(date__month=month)
        
        if year:
            queryset = queryset.filter(date__year=year)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset.order_by('-date', 'employee__name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = AttendanceFilterForm(self.request.GET)
        
        # Add employees for filter dropdown
        context['employees'] = Employee.objects.filter(status=True).order_by('name')
        
        # Pagination
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        
        try:
            attendances = paginator.page(page)
        except PageNotAnInteger:
            attendances = paginator.page(1)
        except EmptyPage:
            attendances = paginator.page(paginator.num_pages)
        
        context['attendances'] = attendances
        context['attendance'] = attendances  # Alias for template compatibility
        
        # Summary statistics
        context['total_present'] = self.get_queryset().filter(status='present').count()
        context['total_absent'] = self.get_queryset().filter(status='absent').count()
        context['total_late'] = self.get_queryset().filter(late_minutes__gt=0).count()
        
        return context


class AttendanceCreateView(AttendanceMixin, CreateView):
    """
    Create new attendance record.
    """
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance/attendance_form.html'
    success_url = reverse_lazy('attendance:attendance_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.filter(status=True).order_by('name')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Attendance created successfully.')
        return super().form_valid(form)


class AttendanceUpdateView(AttendanceMixin, UpdateView):
    """
    Update existing attendance record.
    """
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance/attendance_form.html'
    success_url = reverse_lazy('attendance:attendance_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.filter(status=True).order_by('name')
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Attendance updated successfully.')
        return super().form_valid(form)


class AttendanceDeleteView(AttendanceMixin, DeleteView):
    """
    Delete attendance record.
    """
    model = Attendance
    template_name = 'attendance/attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance:attendance_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Attendance deleted successfully.')
        return super().form_valid(form)


@require_http_methods(["GET"])
def get_employee_attendance(request, employee_id):
    """
    Get attendance data for a specific employee.
    """
    try:
        employee = Employee.objects.get(pk=employee_id)
        date = request.GET.get('date')
        
        if date:
            attendance = Attendance.objects.get(employee=employee, date=date)
            return JsonResponse({
                'success': True,
                'data': {
                    'check_in_time': attendance.check_in_time.strftime('%H:%M') if attendance.check_in_time else None,
                    'check_out_time': attendance.check_out_time.strftime('%H:%M') if attendance.check_out_time else None,
                    'break_duration': attendance.break_duration.total_seconds() / 60 if attendance.break_duration else 0,
                    'status': attendance.status,
                    'late_minutes': attendance.late_minutes,
                    'early_leave_minutes': attendance.early_leave_minutes,
                }
            })
        
        return JsonResponse({'success': False, 'error': 'Date required'})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'})
    except Attendance.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No attendance record'})


@require_http_methods(["POST"])
def bulk_attendance_create(request):
    """
    Create multiple attendance records at once.
    """
    if not request.user.is_admin and not request.user.is_hr:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    date = request.POST.get('date')
    employee_ids = request.POST.getlist('employee_ids')
    check_in = request.POST.get('check_in_time')
    check_out = request.POST.get('check_out_time')
    break_duration = int(request.POST.get('break_duration', 0))
    status = request.POST.get('status', 'present')
    
    if not date or not employee_ids:
        return JsonResponse({'success': False, 'error': 'Date and employees required'})
    
    created_count = 0
    for emp_id in employee_ids:
        employee = Employee.objects.get(pk=emp_id)
        attendance, created = Attendance.objects.update_or_create(
            employee=employee,
            date=date,
            defaults={
                'check_in_time': check_in if check_in else None,
                'check_out_time': check_out if check_out else None,
                'break_duration': timedelta(minutes=break_duration) if break_duration else None,
                'status': status,
            }
        )
        if created:
            created_count += 1
    
    return JsonResponse({'success': True, 'created': created_count})


def attendance_calendar_view(request):
    """
    Display attendance calendar view.
    """
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    employee_id = request.GET.get('employee')
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = timezone.now().year
        month = timezone.now().month
    
    # Get all employees
    employees = Employee.objects.filter(status=True)
    if employee_id:
        employees = employees.filter(pk=employee_id)
    
    # Get attendance for the month
    _, num_days = monthrange(year, month)
    start_date = date_obj(year, month, 1)
    end_date = date_obj(year, month, num_days)
    
    attendances = Attendance.objects.filter(
        employee__in=employees,
        date__gte=start_date,
        date__lte=end_date
    ).select_related('employee')
    
    # Create calendar data
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)
    
    calendar_data = []
    for week in month_days:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': 0, 'attendances': []})
            else:
                current_date = date_obj(year, month, day)
                day_attendances = attendances.filter(date=current_date)
                week_data.append({
                    'day': day,
                    'date': current_date,
                    'attendances': list(day_attendances.values('employee__name', 'status', 'late_minutes'))
                })
        calendar_data.append(week_data)
    
    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'calendar_data': calendar_data,
        'employees': Employee.objects.filter(status=True),
        'selected_employee': employee_id,
    }
    
    return render(request, 'attendance/attendance_calendar.html', context)
