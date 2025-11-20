from django.urls import path 
from . import views


urlpatterns = [
    # This is for fetching all company's departments
    path('departments/', views.DepartmentListAPIView.as_view()),

    # This is for fetching the details of a specific department using the primary key (department_id).
    path('departments/<int:pk>', views.DepartmentDetailAPIView.as_view()),

    # Fetching or creating employees.
    path('employees/', views.EmployeeListCreateAPIView.as_view()),
    
    # Fetching a specific employee data with primary key (employee_id).
    path('employees/<int:pk>', views.EmployeeDetailsAPIView.as_view()),

    # This is for fetching an employee profile instance with all its data.
    path('employees/me/', views.EmployeeProfileAPIView.as_view(), name='employee-profile'),

    # Fetching all employee positions there are in the company.
    path('employees/positions/', views.EmployeePositionAPIView.as_view()),

    # Fetching all employees under specific department, this is for the ManagerDashboard.jsx
    path('department-employees/', views.DepartmentEmployeeListView.as_view(), name='api_department_employees'),

    # This is for handling task operations by the manager himself.
    path('manager-tasks/', views.ManagerTaskListCreateView.as_view(), name='api_manager_tasks'),

    path('tasks/', views.TaskListCreateAPIView.as_view(), name='employee-tasks'),
    path('tasks/<int:pk>/', views.TaskDetailAPIView.as_view(), name='employee-tasks'),

    # This dynamically switches between Dashboard.jsx and ManagerDashboard.jsx
    path('my-dashboard', views.my_dashboard_redirect, name='api_my_dashboard_redirect'),

    # These are for handling file operations.
    path("tasks/<int:task_id>/files/", views.TaskFileListView.as_view(), name="task-files"),
    path("tasks/<int:task_id>/upload-file/", views.TaskFileUploadView.as_view(), name="task-file-upload"),
    path("tasks/<int:task_id>/files/<int:file_id>/", views.TaskFileDeleteView.as_view(), name="task-file-delete"),
]