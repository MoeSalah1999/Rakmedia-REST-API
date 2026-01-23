import random
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from api.models import Company, Department, Employee, EmployeeType, JobRole, EmployeePosition

User = get_user_model()


@pytest.fixture
def company(db):
    return Company.objects.create(name='Test Company')

@pytest.fixture
def department(company):
    return Department.objects.create(name='Engineering', company=company)

@pytest.fixture
def manager_employee(company, department):
    user = User.objects.create_user(
        username='manager',
        password='pass1234',
        role='manager',
        is_staff=True,
    )

    emp_type = EmployeeType.objects.create(name='manager')
    job_role = JobRole.objects.create(name='designer', company=company)

    position = EmployeePosition.objects.create(
        job_role=job_role,
        employee_type=emp_type,
    )

    employee = Employee.objects.create(
        user=user,
        first_name='Manager',
        last_name='User',
        company=company,
        employee_code=random.randint(100, 999),
        position=position,
    )

    employee.department.set([department])
    return employee


@pytest.fixture
def employee(company, department):
    user = User.objects.create_user(
        username='employee',
        password='pass1234',
        role='employee',
    )

    emp_type = EmployeeType.objects.create(name='employee')
    job_role = JobRole.objects.create(name='Developer', company=company)

    position = EmployeePosition.objects.create(
        user=user,
        first_name='Employee',
        last_name='User',
        company=company,
        employee_code=random.randint(100, 900),
        position=position,
    )

    employee.department.set([department])
    return employee

