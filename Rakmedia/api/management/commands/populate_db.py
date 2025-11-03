
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random

from api.models import (
    Company,
    Department,
    EmployeeType,
    JobRole,
    EmployeePosition,
    Employee
)


class Command(BaseCommand):
    help = "Populates the database with sample data ."

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker()

        # Clear old data (optional for dev)
        Employee.objects.all().delete()
        EmployeePosition.objects.all().delete()
        JobRole.objects.all().delete()
        Department.objects.all().delete()
        EmployeeType.objects.all().delete()
        Company.objects.all().delete()

        # 1️⃣ Create company
        company = Company.objects.create(
            name="Rakmedia",
            description="A digital and creative solutions company."
        )
        self.stdout.write(self.style.SUCCESS("✔ Company created."))

        # 2️⃣ Departments (still linked to Employee)
        departments = ["Creative", "Tech", "HR", "Financial", "PR"]
        department_objs = [
            Department.objects.create(name=d, company=company)
            for d in departments
        ]
        self.stdout.write(self.style.SUCCESS("✔ Departments created."))

        # 3️⃣ Employee Types
        emp_type_objs = {
            name: EmployeeType.objects.create(name=name)
            for name in ["Officer", "Manager", "White Collar", "Blue Collar"]
        }
        self.stdout.write(self.style.SUCCESS("✔ Employee types created."))

        # 4️⃣ Job Roles (no department link)
        job_roles = [
            "CEO", "CTO", "CFO", "COO", "CMO",
            "Finance Manager", "HR Manager", "PR Manager", "Creative Manager", "Project Manager"
            "Backend Developer", "ERP System Engineer", "UI/UX Designer",
            "Graphic Designer", "Social Media Manager", "Photographer",
            "Videographer", "Montage", "Driver", "Cleaner", "Technician"
        ]

        job_role_objs = [JobRole.objects.create(name=role, company=company) for role in job_roles]
        role_map = {jr.name: jr for jr in job_role_objs}
        self.stdout.write(self.style.SUCCESS("✔ Job roles created."))

        # 5️⃣ Employee Positions (JobRole ↔ EmployeeType)
        position_map = {
            "Officer": ["CEO", "CTO", "CFO", "COO", "CMO"],
            "Manager": ["Finance Manager", "HR Manager", "PR Manager", "Creative Manager", "Project Manager"],
            "White Collar": ["Backend Developer", "ERP System Engineer", "UI/UX Designer",
                             "Graphic Designer", "Social Media Manager", "Photographer", "Videographer", "Montage"],
            "Blue Collar": ["Driver", "Cleaner", "Technician"]
        }

        position_objs = []
        for etype, role_names in position_map.items():
            for role_name in role_names:
                role = role_map.get(role_name)
                if role:
                    pos = EmployeePosition.objects.create(
                        job_role=role,
                        employee_type=emp_type_objs[etype]
                    )
                    position_objs.append(pos)
        self.stdout.write(self.style.SUCCESS("✔ Employee positions created."))

        # 6️⃣ Employees
        for _ in range(20):
            first = fake.first_name()
            last = fake.last_name()
            employee = Employee.objects.create(
                first_name=first,
                last_name=last,
                email=f"{first.lower()}.{last.lower()}@rakmedia.com",
                company=company,
                position=random.choice(position_objs),
                hire_date=fake.date_between(start_date="-2y", end_date="today"),
                salary=round(random.uniform(1200, 5000), 2),
            )
            employee.department.add(random.choice(department_objs))

        self.stdout.write(self.style.SUCCESS("🎉 Successfully populated 20 employees."))
