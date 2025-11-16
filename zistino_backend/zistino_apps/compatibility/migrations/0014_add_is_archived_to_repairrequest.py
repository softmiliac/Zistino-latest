# Generated manually for adding is_archived field to RepairRequest

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compatibility', '0013_repairrequestmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='repairrequest',
            name='is_archived',
            field=models.BooleanField(default=False, help_text='Whether the repair request is archived'),
        ),
    ]

