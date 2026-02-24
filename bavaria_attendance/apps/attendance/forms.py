from django import forms
from .models import Attendance
from apps.employees.models import Employee


class AttendanceForm(forms.ModelForm):
    """
    Form for creating and updating attendance.
    """
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'check_in_time', 'check_out_time', 'break_duration', 'status', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_in_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'break_duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutes'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(status=True)


class AttendanceFilterForm(forms.Form):
    """
    Form for filtering attendance.
    """
    STATUS_CHOICES = (('', 'All Status'), ('present', 'Present'), ('absent', 'Absent'), ('leave', 'On Leave'))
    
    employee = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee Name'}))
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))


class BulkAttendanceForm(forms.Form):
    """
    Form for bulk attendance entry.
    """
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    employees = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple
    )
    status = forms.ChoiceField(choices=Attendance.STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
