from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, date
from calendar import monthrange
import calendar

from apps.employees.models import Employee
from apps.attendance.models import Attendance
from apps.leave_management.models import Leave
from apps.holidays.models import Holiday, get_holidays_for_month, is_friday, count_fridays_in_month
from .services import SalaryCalculationService, calculate_monthly_salary


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Centralized Dashboard with all modules visible.
    """
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current date or filtered date
        year = self.request.GET.get('year', timezone.now().year)
        month = self.request.GET.get('month', timezone.now().month)
        employee_id = self.request.GET.get('employee')
        category = self.request.GET.get('category')
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            year = timezone.now().year
            month = timezone.now().month
        
        context['selected_year'] = year
        context['selected_month'] = month
        context['selected_employee'] = employee_id
        context['selected_category'] = category
        
        # Get employees for filter
        employees = Employee.objects.filter(status=True).order_by('name')
        if category:
            employees = employees.filter(category=category)
        
        context['employees'] = employees
        
        # Years and months for filters
        current_year = timezone.now().year
        context['years'] = range(current_year - 2, current_year + 3)
        context['months'] = [(m, calendar.month_name[m]) for m in range(1, 13)]
        
        # Calculate month info
        _, num_days = monthrange(year, month)
        context['total_days'] = num_days
        context['month_name'] = calendar.month_name[month]
        
        # Define date range at the beginning - used for all queries
        start_date = date(year, month, 1)
        end_date = date(year, month, num_days)
        
        # If specific employee selected
        if employee_id:
            try:
                employee = Employee.objects.get(pk=employee_id)
                salary_service = SalaryCalculationService(employee, year, month)
                salary_data = salary_service.calculate_salary()
                context['salary_data'] = salary_data
                context['selected_employee_obj'] = employee
            except Employee.DoesNotExist:
                employee = None
        else:
            # Show summary for all employees
            active_employees = Employee.objects.filter(status=True)
            context['total_employees'] = active_employees.count()
            context['total_gross_salary'] = sum(e.gross_salary for e in active_employees)
            
            # Attendance summary for all
            context['total_present'] = Attendance.objects.filter(
                date__gte=start_date, date__lte=end_date, status='present'
            ).values('employee').distinct().count()
            
            context['total_absent'] = Attendance.objects.filter(
                date__gte=start_date, date__lte=end_date, status='absent'
            ).values('employee').distinct().count()
            employee = None
        
        # Get holidays for calendar
        holidays = get_holidays_for_month(year, month)
        context['holidays'] = holidays
        
        # Get leaves for calendar (filter by employee if selected)
        leaves = Leave.objects.filter(
            date__gte=start_date, date__lte=end_date, status='approved'
        )
        if employee_id:
            leaves = leaves.filter(employee_id=employee_id)
        
        # Create a dictionary of leaves by date
        leaves_by_date = {}
        for leave in leaves:
            if leave.date not in leaves_by_date:
                leaves_by_date[leave.date] = []
            leaves_by_date[leave.date].append(leave)
        
        # Get attendance for calendar
        attendances = Attendance.objects.filter(
            date__gte=start_date, date__lte=end_date
        )
        if employee_id:
            attendances = attendances.filter(employee_id=employee_id)
        
        # Create a dictionary of attendance by date
        attendance_by_date = {}
        for att in attendances:
            attendance_by_date[att.date] = att
        
        # Calendar data - use Sunday as first day of week
        cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
        month_days = cal.monthdayscalendar(year, month)
        
        calendar_data = []
        for week in month_days:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append({'day': 0, 'is_holiday': False})
                else:
                    current_date = date(year, month, day)
                    is_holiday = current_date in holidays
                    has_leave = current_date in leaves_by_date
                    has_attendance = current_date in attendance_by_date
                    
                    week_data.append({
                        'day': day,
                        'date': current_date,
                        'is_holiday': is_holiday,
                        'holiday': holidays.get(current_date) if is_holiday else None,
                        'is_friday': is_friday(current_date),
                        'has_leave': has_leave,
                        'leaves': leaves_by_date.get(current_date, []),
                        'has_attendance': has_attendance,
                        'attendance': attendance_by_date.get(current_date) if has_attendance else None
                    })
            calendar_data.append(week_data)
        
        context['calendar_data'] = calendar_data
        
        # Chart data
        context['chart_data'] = self.get_chart_data(year, month, employee_id)
        
        return context
    
    def get_chart_data(self, year, month, employee_id=None):
        """Get chart data for dashboard."""
        _, num_days = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, num_days)
        
        # Present vs Absent Pie Chart
        if employee_id:
            present = Attendance.objects.filter(
                employee_id=employee_id, date__gte=start_date, date__lte=end_date, status='present'
            ).count()
            absent = Attendance.objects.filter(
                employee_id=employee_id, date__gte=start_date, date__lte=end_date, status='absent'
            ).count()
            leave = Attendance.objects.filter(
                employee_id=employee_id, date__gte=start_date, date__lte=end_date, status='leave'
            ).count()
        else:
            present = Attendance.objects.filter(
                date__gte=start_date, date__lte=end_date, status='present'
            ).count()
            absent = Attendance.objects.filter(
                date__gte=start_date, date__lte=end_date, status='absent'
            ).count()
            leave = Attendance.objects.filter(
                date__gte=start_date, date__lte=end_date, status='leave'
            ).count()
        
        # Leave Type Bar Chart
        leave_types = ['SL', 'CL', 'PL', 'ML', 'LWP', 'WL']
        leave_counts = []
        
        for lt in leave_types:
            if employee_id:
                count = Leave.objects.filter(
                    employee_id=employee_id, date__gte=start_date, date__lte=end_date,
                    status='approved', leave_type=lt
                ).count()
            else:
                count = Leave.objects.filter(
                    date__gte=start_date, date__lte=end_date, status='approved', leave_type=lt
                ).count()
            leave_counts.append(count)
        
        return {
            'present_vs_absent': {
                'labels': ['Present', 'Absent', 'Leave'],
                'data': [present, absent, leave]
            },
            'leave_types': {
                'labels': leave_types,
                'data': leave_counts
            }
        }


def dashboard_api(request):
    """
    AJAX API for dashboard data.
    """
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    employee_id = request.GET.get('employee')
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        return JsonResponse({'error': 'Invalid date'}, status=400)
    
    _, num_days = monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)
    
    response_data = {
        'year': year,
        'month': month,
        'total_days': num_days,
    }
    
    if employee_id:
        try:
            employee = Employee.objects.get(pk=employee_id)
            salary_service = SalaryCalculationService(employee, year, month)
            salary_data = salary_service.calculate_salary()
            
            response_data.update({
                'salary': {
                    'gross_salary': str(salary_data['gross_salary']),
                    'working_days': salary_data['working_days'],
                    'present_days': salary_data['present_days'],
                    'absent_days': salary_data['absent_days'],
                    'late_minutes': salary_data['late_minutes'],
                    'early_leave_minutes': salary_data['early_leave_minutes'],
                    'break_late_minutes': salary_data['break_late_minutes'],
                    'done_duty_hours': salary_data['done_duty_hours'],
                    'due_duty_hours': salary_data['due_duty_hours'],
                    'lwp_days': salary_data['lwp_days'],
                    'lwp_deduction': str(salary_data['lwp_deduction']),
                    'late_penalty': str(salary_data['late_penalty']),
                    'final_salary': str(salary_data['final_salary']),
                    'per_day_salary': str(salary_data['per_day_salary']),
                    'leave_summary': salary_data['leave_summary'],
                }
            })
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found'}, status=404)
    else:
        # All employees summary
        active_employees = Employee.objects.filter(status=True)
        response_data['total_employees'] = active_employees.count()
        response_data['total_gross_salary'] = str(sum(e.gross_salary for e in active_employees))
    
    return JsonResponse(response_data)


class SalaryReportView(LoginRequiredMixin, TemplateView):
    """
    Salary Report View.
    """
    template_name = 'dashboard/salary_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        year = self.request.GET.get('year', timezone.now().year)
        month = self.request.GET.get('month', timezone.now().month)
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            year = timezone.now().year
            month = timezone.now().month
        
        employees = Employee.objects.filter(status=True).order_by('name')
        salary_data = []
        
        for employee in employees:
            service = SalaryCalculationService(employee, year, month)
            data = service.calculate_salary()
            salary_data.append(data)
        
        context['employees_salary'] = salary_data
        context['selected_year'] = year
        context['selected_month'] = month
        context['month_name'] = calendar.month_name[month]
        
        # Years and months for filters
        current_year = timezone.now().year
        context['years'] = range(current_year - 2, current_year + 3)
        context['months'] = [(m, calendar.month_name[m]) for m in range(1, 13)]
        
        return context
