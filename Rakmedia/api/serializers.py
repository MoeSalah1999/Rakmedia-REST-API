from rest_framework import serializers
from .models import Company, Department, Employee, EmployeeType, JobRole, EmployeePosition, User, Task, TaskFile




# Basic Company serializer
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'name',
        )



# Basic Department Serializer
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = (
            'id',
            'name',
        )



# Nested-serializer for Employee Type
class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeType
        fields = (
            'id',
            'name',
        )



# Nested-serializer for job role.
class JobRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRole
        fields = (
            'name',

        )



# This is for serializing an employee's position ( Employee Type + Employee Role/job_role )
class EmployeePositionSerializer(serializers.ModelSerializer):
    job_role_name = serializers.CharField(source='job_role.name', read_only=True)
    employee_type_name = serializers.CharField(source='employee_type.name', read_only=True)
    display_name = serializers.SerializerMethodField()

    def get_display_name(self, obj):
        return f'{obj.job_role.name} ({obj.employee_type.name})'

    class Meta:
        model = EmployeePosition
        fields = (
            'id',
            'display_name',
            'job_role_name',
            'employee_type_name',
        )



# This is for serializing an employee's full nested data
class EmployeeDetailSerializer(serializers.ModelSerializer):
    employee_code = serializers.CharField( source='formatted_employee_code', read_only=True )
    job_role = serializers.CharField( source='position.job_role.name', read_only=True )
    employee_type = serializers.CharField( source='position.employee_type.name', read_only=True )
    department = serializers.SlugRelatedField( many=True, slug_field='name', read_only=True )
    username = serializers.CharField( source='user.username', read_only=True )
    user_email = serializers.EmailField( source='user.email' )
    role = serializers.SerializerMethodField()

    def get_role(self, obj):
        # Returns a normalized, lowercase role based on the employee_type.
        # Used by the frontend to determine dashboard and access logic
        
        try:
            employee_type = obj.position.employee_type.name.lower()
            # Normalize synonyms for consistency
            if employee_type in ['manager', 'officer']:
                return employee_type
            elif employee_type in ['white collar', 'blue collar']:
                return 'employee'
            return employee_type
        except AttributeError:
            return 'employee' # fallback if position/employee_type is missing

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return (request.build_absolute_uri(obj.profile_picture.url))
        return None

    class Meta:
        model = Employee
        fields = (
            'id',
            'employee_code',
            'username',
            'first_name',
            'last_name',
            'user_email',
            'job_role',
            'employee_type',
            'hire_date',
            'salary',
            'department',
            'profile_picture',
            'role',
        )
    

    def update(self, instance, validated_data):
        
        # Handle nested updates (If user email or image gets updated)
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Handle profile_picture update
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data['profile_picture']

        # Handle other Employee fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



# This is just for fetching (GET) a specific employee.
class EmployeeGetSerializer(serializers.ModelSerializer):
    employee_code = serializers.CharField(source='formatted_employee_code', read_only=True)
    username = serializers.CharField(source= 'user.username', read_only=True)
    
    class Meta:
        model = Employee
        fields = (
            'id',
            'employee_code',
            'username',
            'first_name',
            'last_name',
        )



# This is for positng new employee data.
class EmployeePostSerializer(serializers.ModelSerializer):
    position = serializers.PrimaryKeyRelatedField(
        queryset=EmployeePosition.objects.select_related('job_role', 'employee_type').all()
    )

    class Meta:
        model = Employee
        fields = (
            'employee_code',
            'first_name',
            'last_name',
            'email',
            'position',
            'department',
            'hire_date',
            'salary',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Restrict M2M query
        self.fields['department'].queryset = Department.objects.only('id', 'name')

        # Cache position choices for HTML form (only once per request)
        # This is for the classic N+1 Query optimization issue we faced with the EmployeePosition model,
        # Specifically the __str__() method that was causing too many Db hits (3x The amount of employees that are in the DB).
        request = self.context.get('request')
        if request and getattr(request.accepted_renderer, 'format', None) == 'html':
            view = self.context.get('view')
            if not hasattr(view, '_position_choices_cache'):
                view._position_choices_cache = list(
                    EmployeePosition.objects.select_related('job_role', 'employee_type')
                )

            self.fields['position'] = serializers.ChoiceField(
                choices=[
                    (str(pos.id), f'{pos.job_role.name} ({pos.employee_type.name})')
                    for pos in view._position_choices_cache
                ],
                required=True,
                label='Position'
            )


    # --- Field Validations ---
    def validate_employee_code(self, value):
        if not isinstance(value, int) or not (1 <= value <= 999):
            raise serializers.ValidationError('Employee code must consist of exactly 3 digits')
        if Employee.objects.filter(employee_code=value).exists():
            raise serializers.ValidationError('An employee with that code already exists')
        return value


    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError('Email address is required.')
        if Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError('An employee with that email already exists')
        return value


    def validate_salary(self, value):
        if value is None:
            raise serializers.ValidationError('Salary cannot be empty')
        if value <= 0:
            raise serializers.ValidationError('Salary cannot be less than, or equal to zero')
        return value
    

# Serializer for User model aka (Employee Profile)
class UserSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeGetSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'role', 
            'employee_profile',
        ]



# Serializer for task files.
class TaskFileSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = TaskFile
        fields = [
            'id',
            'file',
            'description',
            'uploaded_at',
            'uploaded_by_name',
        ]

    def get_uploaded_by_name(self, obj):
        return (
            f'{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}'
            if obj.uploaded_by else 'Unknown'
        )



class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.user.username', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.user.username', read_only=True)
    files = TaskFileSerializer(many=True, read_only=True)


    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'files', 'assigned_to', 'assigned_to_name',
            'assigned_by', 'assigned_by_name', 'due_date', 'completed', 'created_at',
        ]



