from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='phoneNumber',
            new_name='phone_number',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='isActive',
            new_name='is_active_driver',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='emailConfirmed',
            new_name='email_confirmed',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='imageUrl',
            new_name='image_url',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='companyName',
            new_name='company_name',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='vatNumber',
            new_name='vat_number',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='bankname',
            new_name='bank_name',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='birthdate',
            new_name='birth_date',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='codeMeli',
            new_name='national_id',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='representativeBy',
            new_name='representative_by',
        ),
    ]


