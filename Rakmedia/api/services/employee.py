from api.models import Employee


def is_manager_or_officer(employee) -> bool:
    if not employee or not employee.position or not employee.position.employee_type:
        return False
    return employee.position.employee_type.name.lower() in {"manager", "officer"}