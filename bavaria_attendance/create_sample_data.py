"""
Script to create sample data for testing the Bavaria Attendance System.
Run with: python manage.py shell < create_sample_data.py
"""

import os
import sys
import django
from datetime import date, time, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bavaria_attendance.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from apps.employees.models import Employee
from apps.attendance.models import Attendance
from apps.leave_management.models import Leave
from apps.holidays.models import Holiday

User = get_user_model()

def create_users():
    """Create sample users."""
    print("Creating users...")
    
    # Create admin user
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@bavaria.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        print(f"  Created admin user: admin / admin123")
    else:
        print("  Admin user already exists")
    
    # Create HR user
    if not User.objects.filter(username='hr').exists():
        hr = User.objects.create_user(
            username='hr',
            email='hr@bavaria.com',
            password='hr123',
            first_name='HR',
            last_name='Manager',
            role='hr'
        )
        print(f"  Created HR user: hr / hr123")
    else:
        print("  HR user already exists")
    
    # Create viewer user
    if not User.objects.filter(username='viewer').exists():
        viewer = User.objects.create_user(
            username='viewer',
            email='viewer@bavaria.com',
            password='viewer123',
            first_name='Viewer',
            last_name='User',
            role='viewer'
        )
        print(f"  Created viewer user: viewer / viewer123")
    else:
        print("  Viewer user already exists")

def create_employees():
    """Create sample employees."""
    print("\nCreating employees...")
    
    employees_data = [
        {
            'name': 'Mohammad Rahman',
            'category': '8 hours',
            'gross_salary': 25000.00,
            'department': 'Production',
            'joining_date': date(2023, 1, 15),
            'status': True
        },
        {
            'name': 'Ahmed Hassan',
            'category': '11 hours',
            'gross_salary': 35000.00,
            'department': 'Cutting',
            'joining_date': date(2022, 6, 1),
            'status': True
        },
        {
            'name': 'Fatema Begum',
            'category': '8 hours',
            'gross_salary': 22000.00,
            'department': 'Sewing',
            'joining_date': date(2023, 3, 10),
            'status': True
        },
        {
            'name': 'Kamal Hossain',
            'category': '11 hours',
            'gross_salary': 40000.00,
            'department': 'Finishing',
            'joining_date': date(2021, 9, 5),
            'status': True
        },
        {
            'name': 'Jarina Akter',
            'category': '8 hours',
            'gross_salary': 18000.00,
            'department': 'Quality Control',
            'joining_date': date(2024, 1, 1),
            'status': True
        },
    ]
    
    for emp_data in employees_data:
        emp, created = Employee.objects.get_or_create(
            name=emp_data['name'],
            defaults=emp_data
        )
        if created:
            print(f"  Created employee: {emp.name}")
        else:
            print(f"  Employee already exists: {emp.name}")

def create_holidays(year=2026, month=2):
    """Create sample holidays for the month."""
    print(f"\nCreating holidays for {year}...")
    
    # Get number of days in month
    from calendar import monthrange
    _, num_days = monthrange(year, month)
    
    # Create some holidays
    holidays_data = [
        {'date': date(year, month, 14), 'holiday_type': 'public_holiday', 'name': "Valentine's Day"},
        {'date': date(year, month, 21), 'holiday_type': 'public_holiday', 'name': 'International Mother Language Day'},
    ]
    
    for holiday_data in holidays_data:
        if holiday_data['date'].month == month:
            holiday, created = Holiday.objects.get_or_create(
                date=holiday_data['date'],
                defaults=holiday_data
            )
            if created:
                print(f"  Created holiday: {holiday.name} on {holiday.date}")
            else:
                print(f"  Holiday already exists: {holiday.name}")

def create_attendance(year=2026, month=2):
    """Create sample attendance records for February 2026."""
    print(f"\nCreating attendance records for February {year}...")
    
    employees = Employee.objects.filter(status=True)
    if not employees:
        print("  No employees found. Create employees first.")
        return
    
    from calendar import monthrange
    _, num_days = monthrange(year, month)
    
    # Sample attendance data
    attendance_records = [
        # Employee 1 - Mohammad Rahman (8 hours category)
        {'employee_idx': 0, 'day': 1, 'check_in': '08:55', 'check_out': '17:05', 'break': 45, 'status': 'present'},  # Sunday
        {'employee_idx': 0, 'day': 2, 'check_in': '09:10', 'check_out': '17:00', 'break': 50, 'status': 'present'},  # Monday (late)
        {'employee_idx': 0, 'day': 3, 'check_in': '08:50', 'check_out': '17:10', 'break': 45, 'status': 'present'},
        {'employee_idx': 0, 'day': 4, 'check_in': '08:45', 'check_out': '16:50', 'break': 45, 'status': 'present'},  # Early leave
        {'employee_idx': 0, 'day': 5, 'check_in': '09:00', 'check_out': '17:00', 'break': 60, 'status': 'present'},  # Friday
        {'employee_idx': 0, 'day': 8, 'check_in': '08:55', 'check_out': '17:05', 'break': 45, 'status': 'present'},
        {'employee_idx': 0, 'day': 9, 'check_in': '09:00', 'check_out': '17:00', 'break': 45, 'status': 'present'},
        {'employee_idx': 0, 'day': 10, 'status': 'absent'},
        {'employee_idx': 0, 'day': 11, 'check_in': '08:50', 'check_out': '17:10', 'break': 45, 'status': 'present'},
        {'employee_idx': 0, 'day': 12, 'check_in': '09:00', 'check_out': '17:00', 'break': 45, 'status': 'present'},
        
        # Employee 2 - Ahmed Hassan (11 hours category)
        {'employee_idx': 1, 'day': 1, 'check_in': '07:55', 'check_out': '19:05', 'break': 60, 'status': 'present'},
        {'employee_idx': 1, 'day': 2, 'check_in': '08:00', 'check_out': '19:10', 'break': 60, 'status': 'present'},
        {'employee_idx': 1, 'day': 3, 'check_in': '08:05', 'check_out': '19:00', 'break': 65, 'status': 'present'},
        {'employee_idx': 1, 'day': 4, 'check_in': '07:50', 'check_out': '18:50', 'break': 60, 'status': 'present'},
        {'employee_idx': 1, 'day': 5, 'check_in': '08:00', 'check_out': '19:00', 'break': 60, 'status': 'present'},  # Friday
        {'employee_idx': 1, 'day': 8, 'check_in': '07:55', 'check_out': '19:05', 'break': 60, 'status': 'present'},
        {'employee_idx': 1, 'day': 9, 'status': 'absent'},
        {'employee_idx': 1, 'day': 10, 'check_in': '08:00', 'check_out': '19:00', 'break': 60, 'status': 'present'},
        
        # Employee 3 - Fatema Begum (8 hours category)
        {'employee_idx': 2, 'day': 1, 'check_in': '08:50', 'check_out': '17:00', 'break': 45, 'status': 'present'},
        {'employee_idx': 2, 'day': 2, 'check_in': '09:05', 'check_out': '17:10', 'break': 40, 'status': 'present'},  # Late
        {'employee_idx': 2, 'day': 3, 'check_in': '08:55', 'check_out': '17:05', 'break': 45, 'status': 'present'},
        {'employee_idx': 2, 'day': 4, 'check_in': '08:50', 'check_out': '17:00', 'break': 45, 'status': 'present'},
        {'employee_idx': 2, 'day': 5, 'check_in': '09:00', 'check_out': '17:00', 'break': 45, 'status': 'present'},
        {'employee_idx': 2, 'day': 8, 'check_in': '08:45', 'check_out': '17:15', 'break': 50, 'status': 'present'},
        {'employee_idx': 2, 'day': 9, 'check_in': '08:50', 'check_out': '17:00', 'break': 45, 'status': 'present'},
        {'employee_idx': 2, 'day': 10, 'status': 'leave', 'leave_type': 'SL'},  # Sick leave
        {'employee_idx': 2, 'day': 11, 'check_in': '08:50', 'check_out': '17:00', 'break': 45, 'status': 'present'},
        
        # Employee 4 - Kamal Hossain (11 hours category)
        {'employee_idx': 3, 'day': 1, 'check_in': '07:50', 'check_out': '19:00', 'break': 60, 'status': 'present'},
        {'employee_idx': 3, 'day': 2, 'check_in': '07:55', 'check_out': '19:05', 'break': 60, 'status': 'present'},
        {'employee_idx': 3, 'day': 3, 'check_in': '08:10', 'check_out': '19:20', 'break': 55, 'status': 'present'},  # Late
        {'employee_idx': 3, 'day': 4, 'check_in': '07:50', 'check_out': '19:00', 'break': 60, 'status': 'present'},
        {'employee_idx': 3, 'day': 5, 'check_in': '08:00', 'check_out': '19:00', 'break': 60, 'status': 'present'},
    ]
    
    for record in attendance_records:
        emp = employees[record['employee_idx']]
        record_date = date(year, month, record['day'])
        
        # Skip if it's a Friday (automatic holiday)
        if record_date.weekday() == 4:  # Friday
            continue
        
        attendance, created = Attendance.objects.get_or_create(
            employee=emp,
            date=record_date,
            defaults={
                'check_in_time': time(*map(int, record['check_in'].split(':'))) if 'check_in' in record else None,
                'check_out_time': time(*map(int, record['check_out'].split(':'))) if 'check_out' in record else None,
                'break_duration': timedelta(minutes=record['break']) if 'break' in record else None,
                'status': record.get('status', 'present'),
            }
        )
        if created:
            print(f"  Created attendance for {emp.name} on {record_date}")
    
    print(f"  Created {len(attendance_records)} attendance records")

def create_leaves(year=2026, month=2):
    """Create sample leave records."""
    print(f"\nCreating leave records for February {year}...")
    
    employees = Employee.objects.filter(status=True)
    if not employees:
        return
    
    leaves_data = [
        {'employee_idx': 2, 'day': 10, 'leave_type': 'SL', 'status': 'approved'},  # Fatema - Sick Leave
        {'employee_idx': 4, 'day': 15, 'leave_type': 'CL', 'status': 'approved'},  # Jarina - Casual Leave
        {'employee_idx': 0, 'day': 20, 'leave_type': 'PL', 'status': 'pending'},  # Mohammad - Privilege Leave
    ]
    
    for leave_data in leaves_data:
        emp = employees[leave_data['employee_idx']]
        leave_date = date(year, month, leave_data['day'])
        
        leave, created = Leave.objects.get_or_create(
            employee=emp,
            date=leave_date,
            defaults={
                'leave_type': leave_data['leave_type'],
                'status': leave_data['status'],
                'reason': f'{leave_data["leave_type"]} leave',
            }
        )
        if created:
            print(f"  Created leave for {emp.name} on {leave_date} ({leave_data['leave_type']})")

def main():
    """Main function to create all sample data."""
    print("=" * 60)
    print("Creating Sample Data for Bavaria Attendance System")
    print("=" * 60)
    
    create_users()
    create_employees()
    create_holidays()
    create_attendance()
    create_leaves()
    
    print("\n" + "=" * 60)
    print("Sample Data Creation Complete!")
    print("=" * 60)
    print("\nLogin credentials:")
    print("  Admin: admin / admin123")
    print("  HR: hr / hr123")
    print("  Viewer: viewer / viewer123")
    print("\nTo run the server:")
    print("  python manage.py runserver")

if __name__ == '__main__':
    main()
