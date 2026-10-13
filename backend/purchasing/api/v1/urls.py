# purchasing/urls.py

from django.urls import path, include


urlpatterns = [
    path(
        "tasks/",
        include("purchasing.api.v1.purchase_task.urls"),
    ),
    path(
        "employees/",
        include("purchasing.api.v1.purchase_employees.urls"),
    ),
    path(
        "steps/",
        include("purchasing.api.v1.purchase_steps.urls"),
    ),
    path(
        "task-attachments/",
        include("purchasing.api.v1.purchase_attachments.urls"),
    ),
]