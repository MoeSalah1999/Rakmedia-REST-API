import django_filters
from api.models import Employee, Task, TaskFile


# filter for employees.
class EmployeeFilter(django_filters.FilterSet):
    class Meta:
        model = Employee

        # Add or remove whatever fields you want your filter to have or not have.
        fields = {
            'first_name': ['iexact', 'icontains'],
            'last_name': ['iexact', 'icontains'],
            'email': ['iexact', 'icontains'],
            'salary': ['exact', 'lt', 'gt', 'range'],
            'employee_code': ['exact', 'range'],
        }



# filter for tasks.
#class TaskFilter(django_filters.FilterSet):
    #class Meta:
       # model = Task

        #fields = {
        #    'title': ['exact', 'contains'],
         #   'description': ['contains'],
         #   'due_date': ['exact'],
       # }



# Filter for task files.
#class TaskFileFilter(django_filters.FilterSet):
    #class Meta:
        #model = TaskFile 

        #fields = {
           # 'task': ['exact', 'contains'],
           # 'uploaded_by': ['exact', 'contains'],

        #}