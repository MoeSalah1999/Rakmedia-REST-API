from django.contrib import admin
from django import forms
from .models import Company, Department, EmployeeType, JobRole, EmployeePosition, Employee, User, Task
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html


# Register your models here.



# This is for adding new positions to the company
@admin.register(EmployeePosition)
class EmployeePositionAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'get_job_role', 'get_employee_type' )
    list_select_related = ( 'job_role', 'employee_type' )
    ordering = ['id',]
    list_filter = ('employee_type', 'job_role')

    # Search field
    search_fields = ('job_role__name', 'employee_type__name')

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
    

class TaskInline(admin.TabularInline):
    model = Task
    fk_name = 'assigned_to'
    extra = 1 # show one empty row
    fields = ('title', 'completed', 'assigned_by', 'due_date')

    def save_new_instance(self, form, commit=True):
        obj = super().save_new_instance(form, commit=False)
        if not obj.assigned_by:
            obj.assigned_by = self.parent_object.user
        if commit:
            obj.save()
        return obj

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeAdminForm

    inlines = [TaskInline]

    def get_departments(self, obj):
        return ', '.join([dept.name for dept in obj.department.all()])
    
    # tag-styling for the job_role column
    @admin.display(description="Job Role")
    def get_job_role(self,obj):
        if not obj.position or not obj.position.job_role:
            return "-"
        return format_html(
            "<span style='padding:4px 8px;border-radius:10px;background:#eef;color:#000;' class='job-role-tag'>"
            "{}"
            "</span>",
            obj.position.job_role.name
        )
    
    get_job_role.short_description = "Job Role"

    # This is just to make the formatted_employee_code column pretty
    @admin.display(description="Employee Code", ordering="employee_code")
    def formatted_employee_code(self,obj):
        return f"EMP-{obj.employee_code:03d}"

    get_departments.short_description = 'Department' 

    list_display = ( 
        'formatted_employee_code', 
        'first_name', 
        'last_name', 
        'get_job_role', 
        'get_departments', 
        'hire_date', 
        'salary', 
        'user' 
        )
    
    list_select_related = ( 
        'user',
        'position__job_role', 
        'position__employee_type', 
        'company' 
        )
    
    filter_horizontal = ( 'department', )
    list_filter = (
        'position__employee_type', 
        'position__job_role', 
        'department'
        )
    
    # This is so we can order employees based on their employee code, it also gives a heirarchial concept to the employee code.
    ordering = ( 'employee_code', )

    # Extra security.
    readonly_fields= ( 'formatted_employee_code', 'employee_code')

    # We've optimized queries to minimize database hits, we got the N+1 Query issue earlier because of the output of the EmployeePosition model
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'company',
            'position__job_role',
            'position__employee_type',
            'user',
        ).prefetch_related('department')

    # Just makes it easier to search for an employee
    search_fields = (
        'first_name', 
        'last_name', 
        'employee_code', 
        'user__username', 
        'position__job_role__name'
        )

    list_per_page = 20

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'assigned_to',
        'assigned_by',
        'due_date',
        'completed',
    )

    list_filter = ('completed', 'due_date', 'assigned_to')
    search_fields = (
        'title', 
        'assigned_to__first_name', 
        'assigned_to__last_name'
        )
    ordering = ('completed', 'due_date')


#@admin.register(User)
#class UserAdmin(admin.ModelAdmin):
    #list_display = ('username', 'email', 'role', 'is_admin')


#admin.site.register(User, UserAdmin)
admin.site.register(Company)
admin.site.register(Department)
admin.site.register(EmployeeType)
admin.site.register(JobRole)

