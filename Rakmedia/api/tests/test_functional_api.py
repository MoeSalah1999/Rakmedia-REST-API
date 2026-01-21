import random

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.models import Company, Department, Employee, Task

User = get_user_model()


@pytest.mark.django_db
class TestFunctionalAPI:
    def setup_method(self):
        self.client = APIClient()

        self.company = Company.objects.create(name="Acme")

        self.manager_user = User.objects.create_user(
            username="manager",
            password="pass1234",
            is_staff=True,
        )
        self.employee_user = User.objects.create_user(
            username="employee",
            password="pass1234",
        )

        self.manager = Employee.objects.create(
            user=self.manager_user,
            first_name="Manager",
            last_name="User",
            company=self.company,
            employee_code=f"{random.randint(0, 999):03}",

        )

        self.employee = Employee.objects.create(
            user=self.employee_user,
            first_name="Employee",
            last_name="User",
            company=self.company,
            employee_code=f"{random.randint(0, 999):03}",
        )

        self.department = Department.objects.create(
            name="Engineering",
            company=self.company
        )

        self.manager.department.set([self.department])
        self.employee.department.set([self.department])
        

    def authenticate(self, username, password):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": password},
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_department_list_requires_auth(self):
        response = self.client.get(reverse("department-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_manager_can_create_department(self):
        self.authenticate("manager", "pass1234")
        response = self.client.post(
            reverse("department-list"),
            {"name": "HR"},
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_employee_cannot_create_department(self):
        self.authenticate("employee", "pass1234")
        response = self.client.post(
            reverse("department-list"),
            {"name": "HR"},
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_employee_can_view_assigned_task(self):
        task = Task.objects.create(
            title="Task",
            description="Desc",
            assigned_to=self.employee,
        )

        self.authenticate("employee", "pass1234")
        response = self.client.get(
            reverse("employee-task-detail", args=[task.id])
        )
        assert response.status_code == status.HTTP_200_OK

    def test_employee_cannot_delete_unassigned_task(self):
        other_user = User.objects.create_user("other", password="pass1234")
        other_employee = Employee.objects.create(
            user=other_user,
            first_name="Other",
            last_name="User",
            company=self.company,
            employee_code=f"{random.randint(0, 999):03}",
        )

        task = Task.objects.create(
            title="Private",
            description="Desc",
            assigned_to=other_employee,
        )

        self.authenticate("employee", "pass1234")
        response = self.client.delete(
            reverse("employee-task-detail", args=[task.id])
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
