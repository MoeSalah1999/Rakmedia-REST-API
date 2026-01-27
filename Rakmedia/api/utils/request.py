from rest_framework.exceptions import NotAuthenticated
from api.models import Employee


def get_authenticated_employee(request, *, required=True):
    """
    Returns employee for authenticated user.
    Raises NotAuthenticated if required=True and missing.
    """
    user = request.user
    if not user.is_authenticated:
        if required:
            raise NotAuthenticated()
        return None
    
    employee = Employee.objects.filter(user=user).first()
    if required and not employee:
        raise NotAuthenticated("Employee profile not found")
    
    return employee