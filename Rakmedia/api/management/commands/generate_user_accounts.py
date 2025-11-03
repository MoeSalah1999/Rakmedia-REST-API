import csv
import secrets
import string
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Employee  # adjust the app name if different

User = get_user_model()

class Command(BaseCommand):
    help = "Create user accounts for employees who don't have one, and save credentials to a CSV file."

    def handle(self, *args, **options):
        filename = 'generated_employee_logins.csv'
        employees = Employee.objects.filter(user__isnull=True)

        if not employees.exists():
            self.stdout.write(self.style.WARNING("✅ All employees already have linked user accounts."))
            return

        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['employee_id', 'full_name', 'username', 'password', 'email'])

            for emp in employees:
                # Generate unique username
                base_username = f"{emp.first_name.lower()}.{emp.last_name.lower()}"
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                # Generate random password
                password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))

                # Create user
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=emp.email or f"{username}@example.com",
                    first_name=emp.first_name,
                    last_name=emp.last_name,
                    role='employee',
                )

                # Link user to employee
                emp.user = user
                emp.save()

                # Write credentials to file
                writer.writerow([
                    emp.formatted_employee_code,
                    f"{emp.first_name} {emp.last_name}",
                    username,
                    password,
                    user.email,
                ])

                self.stdout.write(self.style.SUCCESS(f"Created user for {emp.first_name} {emp.last_name} ({username})"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ All credentials saved to {filename}"))
