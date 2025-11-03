import django_filters
from api.models import Employee


class EmployeeFilter(django_filters.FilterSet):
    class Meta:
        model = Employee
        fields = {
            'first_name': ['iexact', 'icontains'],
            'last_name': ['iexact', 'icontains'],
            'email': ['iexact', 'icontains'],
            'salary': ['exact', 'lt', 'gt', 'range'],
            'employee_code': ['exact', 'range'],
        }