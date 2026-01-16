from django import forms
from django.contrib import admin
from django.forms import ModelChoiceField
from django.utils.html import format_html

from .models import (
    Company,
    Department,
    Employee,
    EmployeePosition,
    EmployeeType,
    JobRole,
    Task,
    User,
)

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


class EmployeePositionChoiceField(ModelChoiceField):
    def label_form_instance(self, obj):
        return f"{obj.job_role.name} ({obj.employee_type.name})"


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
    select_related = ('assigned_by',)
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
    
    def get_object(self, request, object_id, from_field=None):
        qs = self.get_queryset(request)
        return qs.select_related(
            'user',
            'company',
            'position__job_role',
            'position__employee_type',
        ).prefetch_related(
            'department'
        ).filter(pk=object_id).first()

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
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'position':
            qs = EmployeePosition.objects.select_related(
                'job_role',
                'employee_type'
            )
            kwargs['queryset'] = qs
            kwargs['form_class'] = EmployeePositionChoiceField

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    get_job_role.short_description = "Job Role"

    # This is just to make the formatted_employee_code column pretty
    @admin.display(description="Employee Code", ordering="employee_code")
    def formatted_employee_code(self,obj):
        return f"EMP-{obj.employee_code:03d}"

    get_departments.short_description = 'Department' 

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + (
                'user__username',
                'first_name',
                'last_name',
                'email',
                'company',
                'department',
                'position',
                'salary',
                'employee_code',
            )
        return self.readonly_fields

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
    
    list_display_links = ('formatted_employee_code', 'first_name', 'last_name')
    date_hierarchy = 'hire_date'

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
        'company',
        'first_name', 
        'last_name',
        'department', 
        'employee_code', 
        'user__username', 
        'position__job_role__name'
        )

    list_per_page = 20

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

    autocomplete_fields = (
        'user',
        'company',
        'department',
        'position',
    )
    

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'assigned_to', 'assigned_by'
        )
    

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

    list_per_page = 20


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_admin')

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ('id', 'name')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ('id', 'name')


@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            'company'
        )
    
admin.site.register(EmployeeType)


