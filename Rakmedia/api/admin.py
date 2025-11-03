from django.contrib import admin
from django import forms
from .models import Company, Department, EmployeeType, JobRole, EmployeePosition, Employee, User, Task
from django.contrib.auth.admin import UserAdmin


# Register your models here.



@admin.register(EmployeePosition)
class EmployeePositionAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'get_job_role', 'get_employee_type' )
    list_select_related = ( 'job_role', 'employee_type' )
    ordering = ['id',]

    def get_job_role(self, obj):
        return obj.job_role.name
    get_job_role.short_description = 'Job Role'


    def get_employee_type(self, obj):
        return obj.employee_type.name
    get_employee_type.short_description = 'Employee Type'



class EmployeeAdminForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

    def clean_position(self):
        position = self.cleaned_data.get('position')
        return position
    


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeAdminForm

    def get_departments(self, obj):
        return ', '.join([dept.name for dept in obj.department.all()])
    
    get_departments.short_description = 'Department' 
    list_display = ( 'formatted_employee_code', 'first_name', 'last_name', 'position', 'get_departments', 'hire_date', 'salary', 'user' )
    list_select_related = ( 'user','position__job_role', 'position__employee_type', 'company' )
    filter_horizontal = ( 'department', )
    ordering = ( 'employee_code', )
    readonly_fields= ( 'formatted_employee_code', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'company',
            'position__job_role',
            'position__employee_type',
            'user',
        ).prefetch_related('department')

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    


#@admin.register(User)
#class UserAdmin(admin.ModelAdmin):
    #list_display = ('username', 'email', 'role', 'is_admin')


#admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(Department)
admin.site.register(EmployeeType)
admin.site.register(JobRole)
admin.site.register(Task)
