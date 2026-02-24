from django import forms
from .models import Holiday


class HolidayForm(forms.ModelForm):
    """
    Form for creating and updating holidays.
    """
    class Meta:
        model = Holiday
        fields = ['date', 'holiday_type', 'name', 'description', 'is_recurring']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'holiday_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Holiday name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HolidayFilterForm(forms.Form):
    """
    Form for filtering holidays.
    """
    HOLIDAY_TYPE_CHOICES = (('', 'All'), ('friday', 'Friday'), ('public_holiday', 'Public Holiday'),
                            ('religion_day', 'Religion Day'), ('company_off', 'Company Off'))
    
    holiday_type = forms.ChoiceField(
        required=False,
        choices=HOLIDAY_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    year = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    month = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    
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
        for y in range(current_year - 2, current_year + 3):
            year_choices.append((y, str(y)))
        self.fields['year'].choices = year_choices
