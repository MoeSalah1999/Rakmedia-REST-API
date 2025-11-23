from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Department, Employee, Task
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


# This is a basic test case to create employees and create corresponding employee-profiles (user accounts)
# creates a department that the employees belong to
# and tests JWT-authentication with login after.
class BaseAPITestCase(APITestCase):
    def setUp(self):
        # Create users
        self.manager_user = User.objects.create_user(username="manager", password="pass1234", is_staff=True)
        self.employee_user = User.objects.create_user(username="employee", password="pass1234")

        # Create employees
        self.manager = Employee.objects.create(user=self.manager_user, role="Manager")
        self.employee = Employee.objects.create(user=self.employee_user, role="Employee")

        # JWT login to get tokens
        self.client = APIClient()
        response = self.client.post(reverse('token_obtain_pair'), {
            "username": "manager",
            "password": "pass1234"
        })
        self.manager_token = response.data['access']

        # Returns created user data
        response = self.client.post(reverse('token_obtain_pair'), {
            "username": "employee",
            "password": "pass1234"
        })
        self.employee_token = response.data['access']

        # Department
        self.department = Department.objects.create(name="Sales")

    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


# Test case to test if managers can create departments with authentication permissions
# and that regular employees cannot create a department.
class DepartmentTests(BaseAPITestCase):
    def test_manager_can_create_department(self):
        self.auth(self.manager_token)
        response = self.client.post(reverse('department-list'), {"name": "Marketing"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Just to be sure.
    def test_employee_cannot_create_department(self):
        self.auth(self.employee_token)
        response = self.client.post(reverse('department-list'), {"name": "Marketing"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# Tests whether or not managers can create tasks
# and employees can view tasks assigned to them, but cannot delete them if they don't have the correct permissions.
class TaskTests(BaseAPITestCase):
    def test_manager_can_create_task(self):
        self.auth(self.manager_token)
        response = self.client.post(reverse('task-list'), {
            "title": "Prepare report",
            "description": "Prepare Q4 report",
            "assigned_to": self.employee.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_employee_can_view_own_tasks(self):
        task = Task.objects.create(title="Do something", description="desc", assigned_to=self.employee)
        self.auth(self.employee_token)
        response = self.client.get(reverse('task-detail', args=[task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_employee_cannot_delete_other_tasks(self):
        other_employee = Employee.objects.create(user=User.objects.create_user("other", "other@x.com", "1234"))
        task = Task.objects.create(title="Another", description="Task", assigned_to=other_employee)
        self.auth(self.employee_token)
        response = self.client.delete(reverse('task-detail', args=[task.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


#Tests whether or not task-related file-upload logic is working.
class FileUploadTests(BaseAPITestCase):
    def test_employee_can_upload_file_to_task(self):
        task = Task.objects.create(title="Upload", description="File", assigned_to=self.employee)
        file = SimpleUploadedFile("test.txt", b"dummy content")
        self.auth(self.employee_token)
        response = self.client.post(reverse('taskfile-upload', args=[task.id]), {'file': file})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthTests(APITestCase):
    def test_jwt_authentication(self):
        user = User.objects.create_user(username="testuser", password="pass1234")
        response = self.client.post(reverse('token_obtain_pair'), {
            "username": "testuser",
            "password": "pass1234"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
