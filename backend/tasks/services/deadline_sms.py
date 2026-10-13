from notifications.sms import send_sms


def send_task_deadline_sms(deadline):
    task = deadline.task

    message = (
        f"کارمند گرامی، مهلت انجام تسک "
        f"«{task.title}» "
        f"در مرحله «{deadline.department_step.name}» "
        f"به پایان رسیده است. "
        f"شما تا 24 ساعت آینده وقت دارید این تسک را انجام دهید، "
        f"در غیر این صورت از شما امتیاز کسر می‌شود."
    )

    employees = (
        task.assigned_employee
        .select_related("user")
        .filter(
            user__is_active=True,
            department_memberships__department_id=task.department_id,
            department_memberships__active=True,
        )
        .distinct()
    )

    for employee in employees:
        if not employee.user.phone_number:
            continue

        send_sms(
            employee.user.phone_number,
            message,
        )