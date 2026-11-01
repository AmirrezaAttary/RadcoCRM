from django.db import migrations, models

import accounts.models.user


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_employee_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=accounts.models.user.user_avatar_upload_path,
                verbose_name='عکس پروفایل',
            ),
        ),
    ]
