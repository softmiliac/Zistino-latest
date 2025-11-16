# Generated manually for RepairRequestMessage model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('compatibility', '0012_repairrequest_models'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RepairRequestMessage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('message', models.TextField(help_text='Message content')),
                ('type', models.IntegerField(choices=[(0, 'User Message'), (1, 'Admin Message'), (2, 'System Message')], default=0, help_text='Message type')),
                ('is_admin', models.BooleanField(default=False, help_text='Whether message is from admin')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('repair_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repair_request_messages', to='compatibility.repairrequest')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repair_request_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Repair Request Message',
                'verbose_name_plural': 'Repair Request Messages',
                'db_table': 'repair_request_messages',
                'ordering': ['-created_at'],
            },
        ),
    ]

