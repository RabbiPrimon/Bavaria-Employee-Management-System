from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Employee Admin interface."""
    list_display = ('name', 'category', 'department', 'gross_salary', 'joining_date', 'status')
    list_filter = ('category', 'status', 'department', 'joining_date')
    search_fields = ('name', 'department')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category')
        }),
        ('Employment Details', {
            'fields': ('department', 'gross_salary', 'joining_date', 'status')
        }),
    )
    
    list_per_page = 20
