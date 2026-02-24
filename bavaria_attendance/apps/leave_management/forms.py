from django import forms
from .models import Leave
from apps.employees.models import Employee


class LeaveForm(forms.ModelForm):
    """Form for creating and updating leaves."""
    class Meta:
        model = Leave
        fields = ['employee', 'date', 'leave_type', 'reason', 'status', 'is_paid']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(status=True)
    
    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        date = cleaned_data.get('date')
        
        # Check for duplicate leave
        if employee and date:
            existing_leave = Leave.objects.filter(employee=employee, date=date)
            if self.instance.pk:
                existing_leave = existing_leave.exclude(pk=self.instance.pk)
            
            if existing_leave.exists():
                raise forms.ValidationError(f"Leave already exists for {employee.name} on {date}")
        
        return cleaned_data


class LeaveFilterForm(forms.Form):
    """Form for filtering leave records."""
    STATUS_CHOICES = (('', 'All'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'))
    LEAVE_TYPE_CHOICES = (('', 'All'), ('SL', 'Sick Leave'), ('CL', 'Casual Leave'), ('PL', 'Privilege Leave'), 
                          ('ML', 'Maternity Leave'), ('LWP', 'Leave Without Pay'), ('WL', 'Wedding Leave'))
    
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(status=True),
        required=False,
        empty_label='All Employees',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    leave_type = forms.ChoiceField(
        required=False,
        choices=LEAVE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    month = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    year = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import calendar
        month_choices = [('', 'All Months')]
        for m in range(1, 13):
            month_choices.append((m, calendar.month_name[m]))
        self.fields['month'].choices = month_choices
        
        from datetime import datetime
        current_year = datetime.now().year
        year_choices = [('', 'All Years')]
        for y in range(current_year - 5, current_year + 2):
            year_choices.append((y, str(y)))
        self.fields['year'].choices = year_choices
