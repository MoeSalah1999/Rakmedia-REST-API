from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.conf import settings



# Create your models here.



# The company model that represents the company as an entity.
# Each company can have multiple departments, job roles, and employees.
# Extremely beneficial for large scalable enterprises, or if there are multiple companies in the same code.
class Company(models.Model):
   
    name = models.CharField(max_length=100, unique=True, )
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name



# Represents a department within the company (e.g. Creative, Tech, HR, PR)
# Each department belongs to one company and can be linked to multiple job roles.
class Department(models.Model):
    
    name = models.CharField(max_length=10, unique=True, blank=True, null=True)
    company = models.ForeignKey (Company, on_delete=models.CASCADE, related_name='departments')


    def __str__(self):
        return f'{self.name}'
    


# Categorizes employee based on work type:
# Ex: Officer, Manager, White Collar, Blue Collar.
class EmployeeType(models.Model):
    
    name = models.CharField(max_length=20, unique=True)


    def __str__(self):
        return self.name
    


# Represents a general job role.
# Examples: Backend Developer, Photographer, Driver, UI/UX Designer.
# Each role can belong to multiple departments and is associated with one company.
class JobRole(models.Model):
    
    name = models.CharField(max_length=30, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_roles')


    def __str__(self):
        return self.name
    


# Connects a job role to an employee type to form a valid position.
# Ex: ( Backend Developer + White Collar ) or ( Mechanic + Blue Collar )
# This ensures only logical combinations of roles and employee types exist
class EmployeePosition(models.Model):
    
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='positions')
    employee_type = models.ForeignKey(EmployeeType, on_delete=models.CASCADE, related_name='positions')

    class Meta:
        unique_together = ('job_role', 'employee_type')

    def __str__(self):
        return f'Position {self.id}'



class Employee(models.Model):

    """
    Represents an individual employee.
    Each employee:
    - belongs to a company
    - optionally linked to a department
    - holds a position (combination of role and type)
    - has a hire date and salary
    """
    user = models.OneToOneField (
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='employee_profile', 
        null=True, 
        blank=True,
        )
    
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True,
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    department = models.ManyToManyField(Department, related_name='employees', blank=True)
    position = models.ForeignKey(EmployeePosition, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    hire_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    employee_code = models.PositiveIntegerField(default=999, unique=True)


    @property
    def formatted_employee_code(self):
        """
        Returns a formatted version of the employee code, e.g. EMP-001.
        """
        if self.employee_code is not None:
            return f'EMP-{self.employee_code:03d}'
        return 'N/A'


    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    
    def clean(self):
        """
        Ensure the employee's position type logically matces the job role.
        """
        if not self.position_id:
            return
        
        position = getattr(self, '_prefetched_objects_cache', {}).get('position') or self.position

        if not position:
            return
        
    
        role_name = self.position.job_role.name.lower()
        emp_type = self.position.employee_type.name.lower()

        role_type_map = {
            'CEO': ['Officer'],
            'CTO': ['Officer'],
            'CMO': ['Officer'],
            'CFO': ['Officer'],
            'COO': ['Officer'],
            'Finance Manager': ['Manager'],
            'HR Manager': ['Manager'],
            'PR Manager': ['Manager'],
            'Creative Manager': ['Manager'],
            'Project Manager': ['Manager', 'Officer'],
            'backend develope': ['white collar'],
            'ui/ux designer': ['white collar'],
            'graphic designer': ['white collar'],
            'social media': ['white collar'],
            'photography': ['white collar'],
            'videography': ['white collar'],
            'montage': ['white collar'],
            'erp system': ['white collar'],
            'cleaner': ['blue collar'],
            'technician/maintenance': ['blue collar'],
            'kitchen staff': ['blue collar'],
            'driver': ['blue collar'],
        }


        allowed_types = role_type_map.get(role_name)
        if allowed_types and emp_type not in allowed_types:
            raise ValidationError(
                f'Invalid role-type combination: {position.job_role.name} cannot be assigned to {position.employee_type.name}.'
            )
    


class User (AbstractUser):
    
    is_admin = models.BooleanField(default='False')
    ROLE_CHOICES = [
        ('officer', 'Officer'),
        ('hr', 'HR'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    #Example Use:
    #   if user.role == 'manager':
    #       show manager dashboard

    def __str__(self):
        return self.username
    

User = get_user_model()


class Task(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        'Employee',
        on_delete = models.CASCADE,
        related_name = 'tasks'
    )
    assigned_by = models.ForeignKey(
        'Employee', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
    )
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title    
    


class TaskFile(models.Model):
    '''
    Represents a file related to a specific task.
    Files can be uploaded by either the manager or the assigned employee.
    '''
    task = models.ForeignKey( 'Task', on_delete=models.CASCADE, related_name='files')
    uploaded_by = models.ForeignKey( 'Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_files')
    file = models.FileField(upload_to='task_files/')
    description = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.file.name} (Task ID: {self.task.id})'