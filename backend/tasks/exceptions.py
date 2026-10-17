from rest_framework.exceptions import APIException, PermissionDenied


class TaskServiceError(APIException):

    status_code = 400
    default_detail = "خطایی در عملیات تسک رخ داده است."
    default_code = "task_service_error"


class ActiveTaskExistsError(TaskServiceError):

    default_detail = "پرونده از قبل یک تسک فعال دارد."
    default_code = "active_task_exists"


class EmployeeNotInDepartmentError(TaskServiceError):

    default_detail = "کارمند انتخاب‌شده عضو دپارتمان نیست."
    default_code = "employee_not_in_department"


class InvalidTaskActionError(TaskServiceError):

    default_detail = "این عملیات در وضعیت فعلی مجاز نیست."
    default_code = "invalid_task_action"


class FirstStepRevertError(TaskServiceError):

    default_detail = "تسک در اولین مرحله است و قابل بازگشت نیست."
    default_code = "first_step_revert"


class NotDepartmentManagerError(PermissionDenied):

    default_detail = "فقط مدیر دپارتمان می‌تواند این عملیات را انجام دهد."
    default_code = "not_department_manager"