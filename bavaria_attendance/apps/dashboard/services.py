"""
Salary Calculation Service Layer.
This module contains all business logic for salary calculations.
"""

from datetime import date, timedelta
from calendar import monthrange
from decimal import Decimal
from typing import Dict, List
from django.utils import timezone
from django.db import models

from apps.employees.models import Employee
from apps.attendance.models import Attendance
from apps.leave_management.models import Leave
from apps.holidays.models import get_holidays_for_month, is_friday, count_fridays_in_month


class SalaryCalculationService:
    """Service class for calculating employee salaries."""
    
    def __init__(self, employee: Employee, year: int, month: int):
        self.employee = employee
        self.year = year
        self.month = month
        self.total_days = monthrange(year, month)[1]
        self.start_date = date(year, month, 1)
        self.end_date = date(year, month, self.total_days)
    
    def get_working_days(self) -> int:
        """Calculate total working days in the month."""
        fridays = count_fridays_in_month(self.year, self.month)
        holidays = get_holidays_for_month(self.year, self.month)
        holiday_count = sum(1 for d, h in holidays.items() if h['type'] != 'friday')
        working_days = self.total_days - fridays - holiday_count
        return max(working_days, 0)
    
    def get_present_days(self) -> int:
        """Get total present days for the month."""
        return Attendance.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date,
            status='present'
        ).count()
    
    def get_absent_days(self) -> int:
        """Get total absent days for the month."""
        return Attendance.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date,
            status='absent'
        ).count()
    
    def get_leave_days(self) -> int:
        """Get total approved leave days for the month."""
        return Leave.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date,
            status='approved'
        ).count()
    
    def get_late_minutes(self) -> int:
        """Get total late minutes for the month."""
        result = Attendance.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date,
            status='present'
        ).aggregate(total_late=models.Sum('late_minutes'))
        return result['total_late'] or 0
    
    def get_early_leave_minutes(self) -> int:
        """Get total early leave minutes for the month."""
        result = Attendance.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date,
            status='present'
        ).aggregate(total_early=models.Sum('early_leave_minutes'))
        return result['total_early'] or 0
    
    def get_break_late_minutes(self) -> int:
        """Calculate break late minutes (minutes late beyond 1 hour break)."""
        attendances = Attendance.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date,
            status='present',
            break_duration__isnull=False
        )
        
        total_break_late = 0
        for att in attendances:
            break_minutes = att.break_duration.total_seconds() / 60
            if break_minutes > 60:
                total_break_late += int(break_minutes - 60)
        
        return total_break_late
    
    def get_done_duty_hours(self) -> float:
        """Calculate total done duty hours."""
        attendances = Attendance.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date,
            status='present'
        )
        
        total_hours = 0
        for att in attendances:
            total_hours += att.total_worked_hours
        
        return round(total_hours, 2)
    
    def get_due_duty_hours(self) -> float:
        """Calculate total due duty hours."""
        working_days = self.get_working_days()
        required_hours = self.employee.required_hours_per_day
        return working_days * required_hours
    
    def get_per_day_salary(self) -> Decimal:
        """Calculate per day salary."""
        working_days = self.get_working_days()
        if working_days == 0:
            return Decimal('0.00')
        return self.employee.gross_salary / working_days
    
    def get_lwp_days(self) -> int:
        """Get total Leave Without Pay days."""
        return Leave.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date,
            status='approved',
            leave_type='LWP'
        ).count()
    
    def get_lwp_deduction(self) -> Decimal:
        """Calculate LWP deduction."""
        lwp_days = self.get_lwp_days()
        per_day = self.get_per_day_salary()
        return lwp_days * per_day
    
    def get_late_penalty(self) -> Decimal:
        """Calculate late penalty."""
        late_minutes = self.get_late_minutes()
        required_daily_minutes = Decimal(str(self.employee.required_hours_per_day * 60))
        per_day = self.get_per_day_salary()
        
        if required_daily_minutes == 0:
            return Decimal('0.00')
        
        late_penalty = Decimal(late_minutes) / required_daily_minutes * per_day
        return round(late_penalty, 2)
    
    def get_leave_summary(self) -> Dict[str, int]:
        """Get leave summary by type."""
        leaves = Leave.objects.filter(
            employee=self.employee,
            date__gte=self.start_date,
            date__lte=self.end_date,
            status='approved'
        )
        
        summary = {'SL': 0, 'CL': 0, 'PL': 0, 'ML': 0, 'LWP': 0, 'WL': 0}
        
        for leave in leaves:
            if leave.leave_type in summary:
                summary[leave.leave_type] += 1
        
        return summary
    
    def calculate_salary(self) -> Dict:
        """Calculate complete salary summary."""
        working_days = self.get_working_days()
        present_days = self.get_present_days()
        absent_days = self.get_absent_days()
        leave_days = self.get_leave_days()
        
        per_day_salary = self.get_per_day_salary()
        lwp_days = self.get_lwp_days()
        lwp_deduction = self.get_lwp_deduction()
        late_penalty = self.get_late_penalty()
        
        gross_salary = self.employee.gross_salary
        final_salary = gross_salary - lwp_deduction - late_penalty
        
        return {
            'employee': self.employee,
            'year': self.year,
            'month': self.month,
            'total_days': self.total_days,
            'working_days': working_days,
            'fridays': count_fridays_in_month(self.year, self.month),
            'holidays': sum(1 for d, h in get_holidays_for_month(self.year, self.month).items() if h['type'] != 'friday'),
            'present_days': present_days,
            'absent_days': absent_days,
            'leave_days': leave_days,
            'late_minutes': self.get_late_minutes(),
            'early_leave_minutes': self.get_early_leave_minutes(),
            'break_late_minutes': self.get_break_late_minutes(),
            'done_duty_hours': self.get_done_duty_hours(),
            'due_duty_hours': self.get_due_duty_hours(),
            'gross_salary': gross_salary,
            'per_day_salary': per_day_salary,
            'lwp_days': lwp_days,
            'lwp_deduction': lwp_deduction,
            'late_penalty': late_penalty,
            'final_salary': final_salary,
            'leave_summary': self.get_leave_summary(),
        }


def calculate_monthly_salary(employee: Employee, year: int, month: int) -> Dict:
    """Calculate monthly salary for an employee."""
    service = SalaryCalculationService(employee, year, month)
    return service.calculate_salary()


def calculate_all_employees_salary(year: int, month: int) -> List[Dict]:
    """Calculate salary for all active employees."""
    employees = Employee.objects.filter(status=True)
    results = []
    
    for employee in employees:
        service = SalaryCalculationService(employee, year, month)
        results.append(service.calculate_salary())
    
    return results
