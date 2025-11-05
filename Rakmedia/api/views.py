from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from .utils.cache_decorator import cache_response
from api.serializers import CompanySerializer, DepartmentSerializer, EmployeeGetSerializer, EmployeePostSerializer, JobRoleSerializer, EmployeePositionSerializer, EmployeeDetailSerializer, TaskSerializer, TaskFileSerializer
from api.models import Company, Department, Employee, EmployeePosition, Task, TaskFile
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, filters, permissions, status
from api.filters import EmployeeFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination




# Create your views here.




class CompanyAPIView(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class DepartmentListAPIView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentDetailAPIView(generics.RetrieveAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer



class EmployeePositionAPIView(generics.ListAPIView):
    queryset = EmployeePosition.objects.all()
    serializer_class = EmployeePositionSerializer



@method_decorator(cache_response('employee_list', timeout=900), name='get')
class EmployeeListCreateAPIView(generics.ListCreateAPIView):
    filterset_class = EmployeeFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
        ]
    search_fields = ['first_name', 'last_name', 'email', 'salary', 'employee_code']
    ordering_fields = ['employee_code']
    ordering = ['employee_code']
    pagination_class = PageNumberPagination
    pagination_class.page_size = 5
    pagination_class.page_size_query_param = 'size'
    pagination_class.max_page_size = 10


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeePostSerializer
        return EmployeeGetSerializer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.method == 'POST':
            return (
                Employee.objects.select_related(
                    'company',
                    'position',
                    'position__job_role',
                    'position__employee_type',
                ).prefetch_related('department')
            )
        #return Employee.objects.only('id', 'employee_code', 'first_name', 'last_name')
            
    
    def perform_create(self, serializer):
        default_company = Company.objects.first()
        serializer.save(company=default_company)



@method_decorator(cache_response('employee_details', timeout=900), name='get')
class EmployeeDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.select_related('user', 'position__job_role', 'position__employee_type').prefetch_related('department')
    serializer_class = EmployeeDetailSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Allow the employee to update their own data
            if self.kwargs.get('pk') == 'me':
                self.permission_classes = [IsAuthenticated]
            else:
                self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
            
    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return Employee.objects.select_related(
                'user',
                'position__job_role',
                'position__employee_type',
            ).prefetch_related('department').get(user=self.request.user)
        return super().get_object()



@method_decorator(cache_response('employee_profile', timeout=900), name='get')
class EmployeeProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        '''
        Returns currently logged in employee's profile
        '''
        employee = Employee.objects.filter(user=request.user).select_related('position__job_role', 'position__employee_type').first()
        if not employee:
            return Response({'detail': 'Employee profile is not found.'}, status=404)
        serializer = EmployeeDetailSerializer(employee, context={'request': request})
        return Response(serializer.data)
    
    def patch(self, request):
        # Allow the logged in user to update their profile
        employee = get_object_or_404(Employee, user=request.user)
        serializer = EmployeeDetailSerializer(employee, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)



@method_decorator(cache_response('task_list', timeout=900), name='get')
class TaskListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        employee = Employee.objects.filter(user=user).first()

        if user.is_superuser or user.is_staff:
            return Task.objects.select_related('assigned_to', 'assigned_by').prefetch_related('files')

        if not employee:
            return Task.objects.none()

        return Task.objects.filter(assigned_to=employee).select_related('assigned_to', 'assigned_by').prefetch_related('files')

    def perform_create(self, serializer):
        employee = Employee.objects.filter(user=self.request.user).first()
        serializer.save(assigned_by=employee)



@method_decorator(cache_response('task_details', timeout=900), name='get')
class TaskDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.select_related('assigned_to', 'assigned_by')
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]



# Get employees under manager's authority
@method_decorator(cache_response('department_employees', timeout=900), name='get')
class DepartmentEmployeeListView(generics.ListAPIView):
    serializer_class = EmployeeGetSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = EmployeeFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['first_name', 'last_name', 'employee_Code', 'email', 'salary']
    ordering_fields = ['employee_code']
    ordering = ['employee_code']

    def get_queryset(self):
        user = self.request.user
        employee = Employee.objects.filter(user=user).select_related('company', 'position__employee_type').prefetch_related('department').first()

        if not employee:
            return Employee.objects.none()
        
        employee_type = (
            employee.position.employee_type.name.lower()
            if employee.position and employee.position.employee_type
            else None
        )

        if employee_type not in ['manager', 'officer']:
            return Employee.objects.none()
        
        # Get employees from same company and departments
        departments = employee.department.all()
        return Employee.objects.filter(
            company=employee.company,
            department__in=departments
        ).exclude(id=employee.id).distinct()
    


# Manager's Tasks
@method_decorator(cache_response('manager_tasks', timeout=900), name='get')
class ManagerTaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        employee = Employee.objects.filter(user=user).first()
        if not employee:
            return Task.objects.none()
        return Task.objects.filter(assigned_by=employee).select_related('assigned_to', 'assigned_by').prefetch_related('files')

    def perform_create(self, serializer):
        employee = Employee.objects.filter(user=self.request.user).first()
        serializer.save(assigned_by=employee)



# Dashboard redirect logic
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_dashboard_redirect(request):
    employee = Employee.objects.filter(user=request.user).select_related(
        "position__employee_type"
    ).first()

    if not employee or not employee.position or not employee.position.employee_type:
        return Response({'redirect_to': '/dashboard/'})  # fallback

    employee_type = employee.position.employee_type.name.lower()
    redirect_url = '/manager-dashboard/' if employee_type in ['manager', 'officer'] else '/dashboard/'

    return Response({'redirect_to': redirect_url})



class TaskFileUploadView(generics.CreateAPIView):
    queryset = TaskFile.objects.all()
    serializer_class = TaskFileSerializer
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        employee = Employee.objects.filter(user=self.request.user).first()
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, pk=task_id)
        serializer.save(uploaded_by=employee, task=task)



@method_decorator(cache_response('task_file', timeout=900), name='get')
class TaskFileListView(generics.ListAPIView):
    serializer_class = TaskFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return TaskFile.objects.filter(task_id=task_id).order_by('-uploaded_at')
    


# Deletes a specific task file if the user is authorized.
# Managers can delete any file related to their own assigned task.
# Employees can delete only their own uploaded files
class TaskFileDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id, file_id):
        
        employee = Employee.objects.filter(user=request.user).first()
        task_file = get_object_or_404(TaskFile, pk=file_id, task_id=task_id)

        # Check permissions
        if not employee:
            return Response({'detail': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        is_manager = (
            employee.position and employee.position.employee_type and
            employee.position.employee_type.name.lower() in ['manager', 'officer']
        )

        if task_file.uploaded_by != employee and not is_manager:
            return Response({'detail': 'You do not have permission to delete this file.'}, status=status.HTTP_403_FORBIDDEN)
        
        task_file.file.delete(save=False) # delete the file from storage
        task_file.delete()
        return Response ({'detail': 'File deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
