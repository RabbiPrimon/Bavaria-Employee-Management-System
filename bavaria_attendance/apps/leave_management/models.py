from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Leave(models.Model):
    """
    Leave model with multiple leave types.
    """
    LEAVE_TYPE_CHOICES = (
        ('SL', 'Sick Leave'),
        ('CL', 'Casual Leave'),
        ('PL', 'Privilege Leave'),
        ('ML', 'Maternity Leave'),
        ('LWP', 'Leave Without Pay'),
        ('WL', 'Wedding Leave'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='leaves'
    )
    date = models.DateField()
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leaves'
        verbose_name = 'Leave'
        verbose_name_plural = 'Leaves'
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['employee', 'date', 'leave_type'], name='unique_leave')
        ]
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['leave_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.employee.name} - {self.leave_type} - {self.date}"
    
    def clean(self):
        if self.date > timezone.now().date():
            raise ValidationError({'date': 'Leave date cannot be in the future.'})
    
    def save(self, *args, **kwargs):
        # Auto-set is_paid based on leave type
        if self.leave_type == 'LWP':
            self.is_paid = False
        else:
            self.is_paid = True
        
        # Auto-approve if user is HR
        if self.status == 'pending' and self.approved_by:
            self.status = 'approved'
            self.approved_date = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_deductible(self):
        """Check if leave is deductible from salary."""
        return self.leave_type == 'LWP'
