from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):
    """
    Form for creating and updating employees.
    """
    class Meta:
        model = Employee
        fields = ['name', 'category', 'gross_salary', 'department', 'joining_date', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'gross_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Gross Salary', 'step_price': '0.01'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EmployeeFilterForm(forms.Form):
    """
    Form for filtering employees.
    """
    CATEGORY_CHOICES = (('', 'All Categories'), ('8 hours', '8 Hours'), ('11 hours', '11 Hours'))
    STATUS_CHOICES = (('', 'All Status'), ('true', 'Active'), ('false', 'Inactive'))
    
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name'}))
    category = forms.ChoiceField(required=False, choices=CATEGORY_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    department = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}))
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
