from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import date as date_obj
from calendar import monthrange
import calendar
from .models import Holiday, get_holidays_for_month, is_friday, count_fridays_in_month
from .forms import HolidayForm, HolidayFilterForm


class HolidayMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to check if user is admin or HR.
    """
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_hr


class HolidayListView(LoginRequiredMixin, ListView):
    """
    List all holidays with filtering.
    """
    model = Holiday
    template_name = 'holidays/holiday_list.html'
    context_object_name = 'holidays'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Holiday.objects.all()
        
        holiday_type = self.request.GET.get('holiday_type')
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        
        if holiday_type:
            queryset = queryset.filter(holiday_type=holiday_type)
        
        if year:
            queryset = queryset.filter(date__year=year)
        
        if month:
            queryset = queryset.filter(date__month=month)
        
        return queryset.order_by('date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = HolidayFilterForm(self.request.GET)
        return context


class HolidayCreateView(HolidayMixin, CreateView):
    """
    Create new holiday.
    """
    model = Holiday
    form_class = HolidayForm
    template_name = 'holidays/holiday_form.html'
    success_url = reverse_lazy('holidays:holiday_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Holiday created successfully.')
        return super().form_valid(form)


class HolidayUpdateView(HolidayMixin, UpdateView):
    """
    Update existing holiday.
    """
    model = Holiday
    form_class = HolidayForm
    template_name = 'holidays/holiday_form.html'
    success_url = reverse_lazy('holidays:holiday_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Holiday updated successfully.')
        return super().form_valid(form)


class HolidayDeleteView(HolidayMixin, DeleteView):
    """
    Delete holiday.
    """
    model = Holiday
    template_name = 'holidays/holiday_confirm_delete.html'
    success_url = reverse_lazy('holidays:holiday_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Holiday deleted successfully.')
        return super().form_valid(form)


def holiday_calendar_view(request):
    """
    Display holiday calendar view.
    """
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = timezone.now().year
        month = timezone.now().month
    
    _, num_days = monthrange(year, month)
    start_date = date_obj(year, month, 1)
    end_date = date_obj(year, month, num_days)
    
    holidays = get_holidays_for_month(year, month)
    
    # Create calendar data
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)
    
    calendar_data = []
    for week in month_days:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': 0, 'is_holiday': False})
            else:
                current_date = date_obj(year, month, day)
                is_holiday = current_date in holidays
                week_data.append({
                    'day': day,
                    'date': current_date,
                    'is_holiday': is_holiday,
                    'holiday': holidays.get(current_date) if is_holiday else None,
                    'is_friday': is_friday(current_date)
                })
        calendar_data.append(week_data)
    
    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'calendar_data': calendar_data,
        'holidays': holidays,
    }
    
    return render(request, 'holidays/holiday_calendar.html', context)
