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

    emp_type, _ = EmployeeType.objects.get_or_create(name='Manager')
    job_role, _ = JobRole.objects.get_or_create(name='designer', company=company)

    position, _ = EmployeePosition.objects.get_or_create(
        job_role=job_role,
        employee_type=emp_type,
    )

    manager = Employee.objects.create(
        user=user,
        first_name='Manager',
        last_name='User',
        company=company,
        employee_code=random.randint(100, 999),
        position=position,
    )

    manager.department.set([department])
    return manager


@pytest.fixture
def employee(company, department):
    user = User.objects.create_user(
        username='employee',
        password='pass1234',
        role='employee',
    )

    emp_type, _ = EmployeeType.objects.get_or_create(name='employee')
    job_role, _ = JobRole.objects.get_or_create(name='Developer', company=company)

    position, _ = EmployeePosition.objects.get_or_create(
        job_role=job_role,
        employee_type=emp_type
    )

    employee = Employee.objects.create(
        user=user,
        first_name='Employee',
        last_name='User',
        company=company,
        employee_code=random.randint(100, 900),
        position=position,
    )
    employee.department.set([department])
    return employee

@pytest.fixture
def other_employee(company, department):
    user = User.objects.create_user(
        username="other",
        password="pass1234",
        role="employee",
    )

    emp_type, _ = EmployeeType.objects.get_or_create(name="employee")
    job_role, _ = JobRole.objects.get_or_create(name="QA", company=company)

    position, _ = EmployeePosition.objects.get_or_create(
        job_role=job_role,
        employee_type=emp_type,
    )

    other_employee = Employee.objects.create(
        user=user,
        first_name="Other",
        last_name="User",
        company=company,
        employee_code=random.randint(100, 999),
        position=position,
    )
    other_employee.department.set([department])
    return other_employee


@pytest.fixture
def authenticated_manager_client(manager_employee):
    client = APIClient()
    response = client.post(
        reverse("token_obtain_pair"),
        {
            "username": manager_employee.user.username,
            "password": "pass1234",
        },
    )
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
    )
    return client


@pytest.fixture
def authenticated_employee_client(employee):
    client = APIClient()
    response = client.post(
        reverse("token_obtain_pair"),
        {
            "username": employee.user.username,
            "password": "pass1234",
        },
    )
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
    )
    return client