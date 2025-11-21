import django_filters
from api.models import Employee



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