from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import time, timedelta


class Attendance(models.Model):
    """
    Attendance model with automatic late and early leave calculation.
    """
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'On Leave'),
    )
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    break_duration = models.DurationField(null=True, blank=True)
    late_minutes = models.IntegerField(default=0)
    early_leave_minutes = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance'
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        ordering = ['-date', '-check_in_time']
        constraints = [
            models.UniqueConstraint(fields=['employee', 'date'], name='unique_attendance')
        ]
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.employee.name} - {self.date} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate late minutes
        if self.check_in_time and self.employee:
            self.calculate_late_minutes()
        
        # Auto-calculate early leave minutes
        if self.check_out_time and self.employee:
            self.calculate_early_leave_minutes()
        
        # Auto-set status based on check_in
        if self.check_in_time and not self.status:
            self.status = 'present'
        
        super().save(*args, **kwargs)
    
    def calculate_late_minutes(self):
        """Calculate late minutes based on office start time."""
        office_start = self.get_office_start_time()
        
        if self.check_in_time and self.check_in_time > office_start:
            # Calculate difference in minutes
            late_delta = datetime.combine(self.date, self.check_in_time) - datetime.combine(self.date, office_start)
            self.late_minutes = int(late_delta.total_seconds() / 60)
        else:
            self.late_minutes = 0
    
    def calculate_early_leave_minutes(self):
        """Calculate early leave minutes based on required working hours."""
        if not self.check_out_time or not self.check_in_time:
            self.early_leave_minutes = 0
            return
        
        # Calculate expected checkout time (8 or 11 hours after check-in)
        check_in = datetime.combine(self.date, self.check_in_time)
        required_hours = self.employee.required_hours_per_day if self.employee else 8
        expected_checkout = check_in + timedelta(hours=required_hours)
        
        if self.check_out_time < expected_checkout.time():
            early_delta = datetime.combine(self.date, expected_checkout.time()) - datetime.combine(self.date, self.check_out_time)
            self.early_leave_minutes = int(early_delta.total_seconds() / 60)
        else:
            self.early_leave_minutes = 0
    
    def get_office_start_time(self):
        """Get office start time based on employee category."""
        if self.employee.category == '8 hours':
            return time(9, 0)  # 9:00 AM
        elif self.employee.category == '11 hours':
            return time(8, 0)  # 8:00 AM
        return time(9, 0)  # Default
    
    @property
    def total_worked_hours(self):
        """Calculate total worked hours."""
        if not self.check_in_time or not self.check_out_time:
            return 0
        
        check_in = datetime.combine(self.date, self.check_in_time)
        check_out = datetime.combine(self.date, self.check_out_time)
        
        worked = check_out - check_in
        
        # Subtract break duration
        if self.break_duration:
            worked = worked - self.break_duration
        
        return worked.total_seconds() / 3600  # Convert to hours
    
    def clean(self):
        if self.date > timezone.now().date():
            raise ValidationError({'date': 'Attendance date cannot be in the future.'})


# Import datetime for the calculation
from datetime import datetime, time, timedelta
