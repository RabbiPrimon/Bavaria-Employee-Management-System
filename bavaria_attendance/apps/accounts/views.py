from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import User
from .forms import UserCreationForm, LoginForm


def login_view(request):
    """
    Custom login view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Custom logout view.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@method_decorator(login_required, name='dispatch')
class UserListView(UserPassesTestMixin, ListView):
    """
    List all users (Admin only).
    """
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_admin
    
    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')


@method_decorator(login_required, name='dispatch')
class UserCreateView(UserPassesTestMixin, CreateView):
    """
    Create new user (Admin only).
    """
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def test_func(self):
        return self.request.user.is_admin
    
    def form_valid(self, form):
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UserPassesTestMixin, UpdateView):
    """
    Update existing user (Admin only).
    """
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')
    
    def test_func(self):
        return self.request.user.is_admin
    
    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class UserDeleteView(UserPassesTestMixin, DeleteView):
    """
    Delete user (Admin only).
    """
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')
    
    def test_func(self):
        return self.request.user.is_admin
    
    def form_valid(self, form):
        messages.success(self.request, 'User deleted successfully.')
        return super().form_valid(form)
