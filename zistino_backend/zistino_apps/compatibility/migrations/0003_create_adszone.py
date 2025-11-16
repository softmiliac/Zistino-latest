# Generated manually for AdsZone model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compatibility', '0002_productgroup_productgroupitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdsZone',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('width', models.IntegerField(default=0, help_text='Zone width in pixels')),
                ('height', models.IntegerField(default=0, help_text='Zone height in pixels')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'ads_zones',
                'verbose_name': 'Ads Zone',
                'verbose_name_plural': 'Ads Zones',
                'ordering': ['-created_at'],
            },
        ),
    ]

