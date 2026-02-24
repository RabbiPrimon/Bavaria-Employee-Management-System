from django.contrib import admin
from .models import Holiday


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    """
    Holiday Admin interface.
    """
    list_display = ('date', 'holiday_type', 'name', 'is_recurring')
    list_filter = ('holiday_type', 'is_recurring', 'date')
    search_fields = ('name', 'description')
    date_hierarchy = 'date'
    ordering = ('-date',)
    
    fieldsets = (
        ('Holiday Information', {
            'fields': ('date', 'holiday_type', 'name', 'description')
        }),
        ('Recurring', {
            'fields': ('is_recurring',)
        }),
    )
    
    list_per_page = 20
