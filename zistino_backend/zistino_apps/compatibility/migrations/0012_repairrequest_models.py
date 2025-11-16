# Generated manually for RepairRequests models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('compatibility', '0011_contactusmessage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RepairRequest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('duration', models.IntegerField(default=0, help_text='Estimated duration in minutes')),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, help_text='Total price', max_digits=10)),
                ('tracking_code', models.CharField(blank=True, help_text='Tracking code for the repair request', max_length=50, null=True, unique=True)),
                ('steps', models.IntegerField(default=0, help_text='Number of steps')),
                ('delivery_information', models.TextField(blank=True, help_text='Delivery information', null=True)),
                ('note', models.TextField(blank=True, help_text='Additional notes', null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('gender', models.IntegerField(choices=[(0, 'Not Specified'), (1, 'Male'), (2, 'Female')], default=0)),
                ('address', models.TextField(blank=True, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=20, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('company_name', models.CharField(blank=True, max_length=255, null=True)),
                ('company_number', models.CharField(blank=True, max_length=50, null=True)),
                ('vat_number', models.CharField(blank=True, max_length=50, null=True)),
                ('user_type', models.IntegerField(choices=[(0, 'Individual'), (1, 'Company')], default=0)),
                ('request_type', models.IntegerField(choices=[(0, 'Standard'), (1, 'Urgent'), (2, 'Emergency')], default=0)),
                ('delivery_mode', models.IntegerField(choices=[(0, 'Pickup'), (1, 'Delivery'), (2, 'On-Site')], default=0)),
                ('delivery_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repair_requests', to='products.product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repair_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Repair Request',
                'verbose_name_plural': 'Repair Requests',
                'db_table': 'repair_requests',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RepairRequestDetail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, help_text='Price for this detail', max_digits=10)),
                ('start_repair_date', models.DateTimeField(blank=True, help_text='Start repair date', null=True)),
                ('end_repair_date', models.DateTimeField(blank=True, help_text='End repair date', null=True)),
                ('is_canceled', models.BooleanField(default=False, help_text='Whether this detail is canceled')),
                ('cancelation_description', models.TextField(blank=True, help_text='Cancellation description', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('problem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repair_request_details', to='products.problem')),
                ('repair_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repair_request_details', to='compatibility.repairrequest')),
            ],
            options={
                'verbose_name': 'Repair Request Detail',
                'verbose_name_plural': 'Repair Request Details',
                'db_table': 'repair_request_details',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='RepairRequestStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.TextField(blank=True, help_text='Status text/description', null=True)),
                ('status', models.IntegerField(choices=[(0, 'Pending'), (1, 'In Progress'), (2, 'Completed'), (3, 'Cancelled')], default=0, help_text='Status code')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('repair_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repair_request_statuses', to='compatibility.repairrequest')),
            ],
            options={
                'verbose_name': 'Repair Request Status',
                'verbose_name_plural': 'Repair Request Statuses',
                'db_table': 'repair_request_statuses',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RepairRequestDocument',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('document', models.FileField(blank=True, help_text='Document file', null=True, upload_to='repair_requests/documents/')),
                ('document_url', models.CharField(blank=True, help_text='Document URL if stored externally', max_length=500, null=True)),
                ('description', models.TextField(blank=True, help_text='Document description', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('repair_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repair_request_documents', to='compatibility.repairrequest')),
            ],
            options={
                'verbose_name': 'Repair Request Document',
                'verbose_name_plural': 'Repair Request Documents',
                'db_table': 'repair_request_documents',
                'ordering': ['-created_at'],
            },
        ),
    ]

