from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Leave
from .forms import LeaveForm, LeaveFilterForm
from apps.employees.models import Employee


class LeaveMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to check if user is admin or HR."""
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_hr


class LeaveListView(LoginRequiredMixin, ListView):
    """List all leave records with filtering."""
    model = Leave
    template_name = 'leave_management/leave_list.html'
    context_object_name = 'leaves'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Leave.objects.select_related('employee').all()
        
        employee = self.request.GET.get('employee')
        leave_type = self.request.GET.get('leave_type')
        status = self.request.GET.get('status')
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        
        if employee:
            queryset = queryset.filter(employee_id=employee)
        
        if leave_type:
            queryset = queryset.filter(leave_type=leave_type)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if month:
            queryset = queryset.filter(date__month=month)
        
        if year:
            queryset = queryset.filter(date__year=year)
        
        return queryset.order_by('-date', 'employee__name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = LeaveFilterForm(self.request.GET)
        # Add employees for filter dropdown
        context['employees'] = Employee.objects.filter(status=True).order_by('name')
        return context


class LeaveCreateView(LeaveMixin, CreateView):
    """Create new leave record."""
    model = Leave
    form_class = LeaveForm
    template_name = 'leave_management/leave_form.html'
    success_url = reverse_lazy('leave:leave_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Leave created successfully.')
        return super().form_valid(form)


class LeaveUpdateView(LeaveMixin, UpdateView):
    """Update existing leave record."""
    model = Leave
    form_class = LeaveForm
    template_name = 'leave_management/leave_form.html'
    success_url = reverse_lazy('leave:leave_list')
    
    def form_valid(self, form):
        leave = form.save(commit=False)
        if leave.status == 'approved' and not leave.approved_by:
            leave.approved_by = self.request.user
            leave.approved_date = timezone.now()
        leave.save()
        messages.success(self.request, 'Leave updated successfully.')
        return super().form_valid(form)


class LeaveDeleteView(LeaveMixin, DeleteView):
    """Delete leave record."""
    model = Leave
    template_name = 'leave_management/leave_confirm_delete.html'
    success_url = reverse_lazy('leave:leave_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Leave deleted successfully.')
        return super().form_valid(form)


@require_http_methods(["POST"])
def approve_leave(request, pk):
    """Approve a leave request."""
    if not request.user.is_admin and not request.user.is_hr:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('leave:leave_list')
    
    leave = get_object_or_404(Leave, pk=pk)
    leave.status = 'approved'
    leave.approved_by = request.user
    leave.approved_date = timezone.now()
    leave.save()
    
    messages.success(request, f'Leave approved for {leave.employee.name}.')
    return redirect('leave:leave_list')


@require_http_methods(["POST"])
def reject_leave(request, pk):
    """Reject a leave request."""
    if not request.user.is_admin and not request.user.is_hr:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('leave:leave_list')
    
    leave = get_object_or_404(Leave, pk=pk)
    leave.status = 'rejected'
    leave.save()
    
    messages.success(request, f'Leave rejected for {leave.employee.name}.')
    return redirect('leave:leave_list')
