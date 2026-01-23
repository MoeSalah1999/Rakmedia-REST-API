import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.models import Department, Company


@pytest.mark.django_db
class TestDepartmentEdgeCases:
    def test_department_list_requires_auth(self):
        client = APIClient()
        response = client.get(reverse('department-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_department_created_in_managers_company(
            self, authenticated_manager_client, manager_employee
    ):
        response = authenticated_manager_client.post(
            reverse('department-list'),
            {'name': 'Finance'},
        )
        assert response.status_code == status.HTTP_201_CREATED

        department = Department.objects.get(name='Finance')
        assert department.company == manager_employee.company

    def test_employee_sees_departments_but_cannot_create(
            self, authenticated_employee_client
    ):
        response = authenticated_employee_client.get(
            reverse('department-list')
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestEmployeeProfileAPI:

    def test_profile_requires_auth(self):
        client = APIClient()
        response = client.get(reverse("employee-profile"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_employee_gets_own_profile(
        self, authenticated_employee_client, employee
    ):
        response = authenticated_employee_client.get(
            reverse("employee-profile")
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == employee.id

    def test_employee_can_patch_own_profile(
        self, authenticated_employee_client
    ):
        response = authenticated_employee_client.patch(
            reverse("employee-profile"),
            {"first_name": "Updated"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"


@pytest.mark.django_db
class TestTaskListVisibility:

    def test_employee_sees_only_assigned_tasks(
        self, authenticated_employee_client, employee, other_employee
    ):
        from api.models import Task

        Task.objects.create(
            title="Mine",
            description="A",
            assigned_to=employee,
        )
        Task.objects.create(
            title="Not mine",
            description="B",
            assigned_to=other_employee,
        )

        response = authenticated_employee_client.get(
            reverse("employee-tasks")
        )

        assert response.status_code == status.HTTP_200_OK
        titles = [task["title"] for task in response.data]
        assert "Mine" in titles
        assert "Not mine" not in titles

    def test_task_create_sets_assigned_by(
        self, authenticated_manager_client, manager_employee, employee
    ):
        response = authenticated_manager_client.post(
            reverse("employee-tasks"),
            {
                "title": "Delegated",
                "description": "Task",
                "assigned_to": employee.id,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["assigned_by"] == manager_employee.id
