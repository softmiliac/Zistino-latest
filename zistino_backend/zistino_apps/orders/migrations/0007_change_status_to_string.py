# Generated manually - Change Order.status from IntegerField to CharField

from django.db import migrations, models


def convert_status_to_string(apps, schema_editor):
    """Convert integer status values to string status values using raw SQL"""
    db_alias = schema_editor.connection.alias
    
    # Map old integer status to new string status using SQL CASE statement
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            UPDATE orders
            SET status = CASE status::text
                WHEN '0' THEN 'pending'
                WHEN '1' THEN 'confirmed'
                WHEN '2' THEN 'in_progress'
                WHEN '3' THEN 'completed'
                WHEN '4' THEN 'cancelled'
                ELSE 'pending'
            END
        """)


def convert_status_to_integer(apps, schema_editor):
    """Reverse migration - convert string status back to integer (for rollback)"""
    db_alias = schema_editor.connection.alias
    
    # Map string status to integer status using SQL CASE statement
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            UPDATE orders
            SET status = CASE status
                WHEN 'pending' THEN '0'
                WHEN 'confirmed' THEN '1'
                WHEN 'in_progress' THEN '2'
                WHEN 'completed' THEN '3'
                WHEN 'cancelled' THEN '4'
                ELSE '0'
            END
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_order_estimated_weight_range_preferred_delivery_date'),
    ]

    operations = [
        # Step 1: Change field type from IntegerField to CharField (temporarily allow any string)
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                default='0',
                max_length=20,
            ),
        ),
        
        # Step 2: Convert integer status values to strings using raw SQL
        migrations.RunPython(convert_status_to_string, convert_status_to_integer),
        
        # Step 3: Update field with choices and proper default
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('confirmed', 'Confirmed'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                ],
                default='pending',
                help_text='Order status: pending, confirmed, in_progress, completed, or cancelled',
                max_length=20,
            ),
        ),
    ]

