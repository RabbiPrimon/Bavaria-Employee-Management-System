from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """
    Attendance Admin interface.
    """
    list_display = ('employee', 'date', 'check_in_time', 'check_out_time', 'late_minutes', 'early_leave_minutes', 'status')
    list_filter = ('status', 'date', 'employee__department', 'employee__category')
    search_fields = ('employee__name', 'employee__employee_id', 'notes')
    date_hierarchy = 'date'
    ordering = ('-date', 'employee__name')
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'date')
        }),
        ('Time Records', {
            'fields': ('check_in_time', 'check_out_time', 'break_duration')
        }),
        ('Calculations', {
            'fields': ('late_minutes', 'early_leave_minutes', 'status')
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
    )
    
    list_per_page = 20
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing record
            return ['late_minutes', 'early_leave_minutes']
        return []
