from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Employee(models.Model):
    """
    Employee model with category, salary, and employment details.
    """
    CATEGORY_CHOICES = (
        ('8 hours', '8 Hours'),
        ('11 hours', '11 Hours'),
    )
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='8 hours')
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    department = models.CharField(max_length=100)
    joining_date = models.DateField()
    status = models.BooleanField(default=True)
    is_repeated = models.BooleanField(default=False, help_text='Mark as duplicate/repeated record')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    @property
    def required_hours_per_day(self):
        """Return required working hours per day based on category."""
        if self.category == '8 hours':
            return 8
        elif self.category == '11 hours':
            return 11
        return 8
    
    @property
    def office_start_time(self):
        """Return office start time based on category."""
        if self.category == '8 hours':
            return '09:00'
        elif self.category == '11 hours':
            return '08:00'
        return '09:00'
    
    @property
    def has_attendances(self):
        """Check if employee has any attendance records."""
        return self.attendances.exists()
    
    @property
    def has_leaves(self):
        """Check if employee has any leave records."""
        return self.leaves.exists()
    
    @property
    def can_delete(self):
        """
        Check if employee can be deleted.
        Allowed if:
        - Employee status is Inactive (status=False)
        - OR Employee is marked as Repeated (is_repeated=True)
        
        Not allowed if:
        - Employee is Active AND has attendance or leave records
        """
        # Allow deletion if employee is inactive OR marked as repeated
        if not self.status or self.is_repeated:
            # But still check for related records as an additional protection
            if self.has_attendances or self.has_leaves:
                return False
            return True
        return False
    
    def get_delete_error_message(self):
        """Return appropriate error message if deletion is not allowed."""
        if self.status and not self.is_repeated:
            if self.has_attendances or self.has_leaves:
                return "Cannot delete active employee with attendance or leave records."
            return "Cannot delete active employee."
        if self.has_attendances or self.has_leaves:
            return "Cannot delete employee with attendance or leave records."
        return None
    
    def clean(self):
        if self.gross_salary < 0:
            raise ValidationError({'gross_salary': 'Salary cannot be negative.'})
