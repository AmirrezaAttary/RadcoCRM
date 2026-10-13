from django.urls import include, path

urlpatterns = [
    path(
        "department/",
        include("department.api.v1.department.urls"),
    ),

    path(
            "department_employee/",
            include("department.api.v1.department_employee.urls"),
        ),

    path(
                "department_step/",
                include("department.api.v1.department_step.urls"),
            ),
]