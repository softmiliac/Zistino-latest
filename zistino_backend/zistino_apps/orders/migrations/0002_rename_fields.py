from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='totalPrice',
            new_name='total_price',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='createOrderDate',
            new_name='create_order_date',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='submitPriceDate',
            new_name='submit_price_date',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='sendToPostDate',
            new_name='send_to_post_date',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='postStateNumber',
            new_name='post_state_number',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='paymentTrackingCode',
            new_name='payment_tracking_code',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='userFullName',
            new_name='user_full_name',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='userPhoneNumber',
            new_name='user_phone_number',
        ),
        migrations.RenameField(
            model_name='orderitem',
            old_name='productName',
            new_name='product_name',
        ),
        migrations.RenameField(
            model_name='orderitem',
            old_name='unitPrice',
            new_name='unit_price',
        ),
        migrations.RenameField(
            model_name='orderitem',
            old_name='totalPrice',
            new_name='total_price',
        ),
    ]


