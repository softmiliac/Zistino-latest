# Generated manually for AdsItem model
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('compatibility', '0003_create_adszone'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdsItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file_path', models.CharField(help_text='Path to the ad file', max_length=500)),
                ('file_type', models.IntegerField(default=0, help_text='Type of file (0=image, 1=video, etc.)')),
                ('from_time', models.DateTimeField(help_text='When the ad starts displaying')),
                ('to_time', models.DateTimeField(help_text='When the ad stops displaying')),
                ('locale', models.CharField(default='en', help_text='Locale code (e.g., fa, en)', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ads_zone', models.ForeignKey(
                    db_column='ads_zone_id',
                    help_text='Foreign key to AdsZone',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ads_items',
                    to='compatibility.adszone'
                )),
            ],
            options={
                'db_table': 'ads_items',
                'verbose_name': 'Ads Item',
                'verbose_name_plural': 'Ads Items',
                'ordering': ['-created_at'],
            },
        ),
    ]

