from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from .models import Employee
from .forms import EmployeeForm, EmployeeFilterForm


class EmployeeMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to check if user is admin or HR.
    """
    def test_func(self):
        return self.request.user.is_admin or self.request.user.is_hr


class EmployeeListView(LoginRequiredMixin, ListView):
    """
    List all employees with pagination and filtering.
    """
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Employee.objects.all()
        
        # Apply filters
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        category = self.request.GET.get('category')
        department = self.request.GET.get('department')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(id__icontains=search) | Q(department__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status == 'true')
        
        if category:
            queryset = queryset.filter(category=category)
        
        if department:
            queryset = queryset.filter(department__icontains=department)
        
        return queryset.select_related()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = EmployeeFilterForm(self.request.GET)
        
        # Pagination
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        
        try:
            employees = paginator.page(page)
        except PageNotAnInteger:
            employees = paginator.page(1)
        except EmptyPage:
            employees = paginator.page(paginator.num_pages)
        
        context['employees'] = employees
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """
    Display employee details.
    """
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'


class EmployeeCreateView(EmployeeMixin, CreateView):
    """
    Create new employee.
    """
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Employee created successfully.')
        return super().form_valid(form)


class EmployeeUpdateView(EmployeeMixin, UpdateView):
    """
    Update existing employee.
    """
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Employee updated successfully.')
        return super().form_valid(form)


class EmployeeDeleteView(EmployeeMixin, DeleteView):
    """
    Delete employee.
    """
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Employee deleted successfully.')
        return super().form_valid(form)


def toggle_employee_status(request, pk):
    """
    Toggle employee status (activate/deactivate).
    """
    if not request.user.is_admin and not request.user.is_hr:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('employees:employee_list')
    
    employee = get_object_or_404(Employee, pk=pk)
    employee.status = not employee.status
    employee.save()
    
    status = 'activated' if employee.status else 'deactivated'
    messages.success(request, f'Employee {status} successfully.')
    return redirect('employees:employee_list')


def delete_employee(request, pk):
    """
    Delete employee with validation logic.
    
    Only allowed if:
    - Employee status is Inactive (status=False)
    - OR Employee is marked as Repeated (is_repeated=True)
    
    Not allowed if:
    - Employee is Active
    - Employee has related Attendance records
    - Employee has related Leave records
    
    Only Admin role can delete employees.
    """
    # Check if user is logged in
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to perform this action.')
        return redirect('login')
    
    # Only Admin can delete employees
    if not request.user.is_admin:
        messages.error(request, 'You do not have permission to delete employees. Only Admin can delete.')
        return redirect('employees:employee_list')
    
    # Get employee object
    employee = get_object_or_404(Employee, pk=pk)
    
    # Check deletion conditions using model's can_delete property
    if not employee.can_delete:
        # Get appropriate error message
        error_message = employee.get_delete_error_message()
        messages.error(request, error_message)
        return redirect('employees:employee_list')
    
    # Get employee name for success message before deletion
    employee_name = employee.name
    
    # Delete the employee
    employee.delete()
    
    # Success message
    messages.success(request, f'Employee "{employee_name}" deleted successfully.')
    
    return redirect('employees:employee_list')
