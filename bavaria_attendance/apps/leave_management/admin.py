from django.contrib import admin
from .models import Leave


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    """
    Leave Admin interface.
    """
    list_display = ('employee', 'date', 'leave_type', 'status', 'is_paid', 'approved_by', 'created_at')
    list_filter = ('status', 'leave_type', 'is_paid', 'date', 'employee__department')
    search_fields = ('employee__name', 'reason')
    date_hierarchy = 'date'
    ordering = ('-date', 'employee__name')
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'date', 'leave_type')
        }),
        ('Leave Details', {
            'fields': ('reason', 'status', 'is_paid')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_date')
        }),
    )
    
    list_per_page = 20
