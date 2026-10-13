from django.urls import path

from .views import TaskAttachmentCreateApi

app_name = "task_attachment"

urlpatterns = [
    path("<int:pk>/attachments/", TaskAttachmentCreateApi.as_view(), name="task-attachment-create"),
]