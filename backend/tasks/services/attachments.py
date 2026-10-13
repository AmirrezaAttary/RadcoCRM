from django.db import transaction

from ..models import TaskAttachment


def _create_attachments(*, files, uploaded_by, task=None, task_step_log=None):
    attachments = []

    for f in files:
        attachment = TaskAttachment(
            task=task,
            task_step_log=task_step_log,
            file=f,
            original_file_name=f.name,
            uploaded_by=uploaded_by,
        )
        attachment.full_clean()
        attachment.save()
        attachments.append(attachment)

    return attachments


@transaction.atomic
def add_task_attachments(*, task, files, uploaded_by):
    return _create_attachments(files=files, uploaded_by=uploaded_by, task=task)