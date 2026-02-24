from django.db import models
from django.core.exceptions import ValidationError
from datetime import date, datetime
from calendar import monthrange


class Holiday(models.Model):
    """
    Holiday model with various holiday types.
    """
    HOLIDAY_TYPE_CHOICES = (
        ('friday', 'Friday'),
        ('public_holiday', 'Public Holiday'),
        ('religion_day', 'Religion Day'),
        ('company_off', 'Company Off'),
    )
    
    date = models.DateField(unique=True)
    holiday_type = models.CharField(max_length=20, choices=HOLIDAY_TYPE_CHOICES)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'holidays'
        verbose_name = 'Holiday'
        verbose_name_plural = 'Holidays'
        ordering = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['holiday_type']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.get_holiday_type_display()}"
    
    def clean(self):
        if self.date.year < 2020:
            raise ValidationError({'date': 'Year must be 2020 or later.'})


def is_friday(check_date):
    """Check if a given date is Friday."""
    return check_date.weekday() == 4  # Monday=0, Friday=4


def get_holidays_for_month(year, month):
    """
    Get all holidays for a specific month.
    Includes both explicit holidays and Fridays.
    """
    _, num_days = monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)
    
    holidays = Holiday.objects.filter(
        models.Q(date__gte=start_date, date__lte=end_date) |
        models.Q(is_recurring=True, date__month=month)
    )
    
    holiday_dates = {}
    for holiday in holidays:
        holiday_dates[holiday.date] = {
            'name': holiday.name,
            'type': holiday.holiday_type,
            'description': holiday.description
        }
    
    # Add Fridays as holidays
    for day in range(1, num_days + 1):
        current_date = date(year, month, day)
        if is_friday(current_date) and current_date not in holiday_dates:
            holiday_dates[current_date] = {
                'name': 'Friday',
                'type': 'friday',
                'description': 'Weekly Holiday'
            }
    
    return holiday_dates


def count_fridays_in_month(year, month):
    """Count the number of Fridays in a month."""
    _, num_days = monthrange(year, month)
    friday_count = 0
    
    for day in range(1, num_days + 1):
        current_date = date(year, month, day)
        if is_friday(current_date):
            friday_count += 1
    
    return friday_count
