"""
Celery tasks for delivery management.
"""
import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from .models import Delivery
from zistino_apps.payments.sms_service import send_delivery_reminder

logger = logging.getLogger(__name__)


@shared_task
def check_and_send_delivery_reminders():
    """
    Periodic task to check for deliveries that need reminder SMS.
    Sends SMS 1 hour before the delivery time period starts.
    
    This task should run every 15-30 minutes to catch all deliveries.
    """
    try:
        now = timezone.now()
        # Calculate the time window: 1 hour from now (with 15 min buffer)
        reminder_start = now + timedelta(minutes=45)  # 45 minutes from now
        reminder_end = now + timedelta(minutes=75)     # 75 minutes from now
        
        logger.info(f"Checking for deliveries needing reminder SMS between {reminder_start} and {reminder_end}")
        
        # Find deliveries that:
        # 1. Have a delivery_date set
        # 2. Are scheduled between reminder_start and reminder_end
        # 3. Haven't had reminder SMS sent yet (reminder_sms_sent=False)
        # 4. Are not cancelled
        deliveries = Delivery.objects.filter(
            delivery_date__isnull=False,
            delivery_date__gte=reminder_start,
            delivery_date__lte=reminder_end,
            reminder_sms_sent=False,
        ).exclude(
            status='cancelled'
        ).select_related('order', 'driver')
        
        sent_count = 0
        failed_count = 0
        
        for delivery in deliveries:
            try:
                # Get customer phone number from order
                phone_number = delivery.phone_number
                if not phone_number:
                    # Fallback to order's customer phone
                    phone_number = getattr(delivery.order, 'phone_number', None)
                    if not phone_number:
                        logger.warning(f"Delivery {delivery.id} has no phone number, skipping SMS")
                        continue
                
                # Send reminder SMS
                success = send_delivery_reminder(
                    phone_number=phone_number,
                    delivery_date=delivery.delivery_date,
                    delivery_id=str(delivery.id)
                )
                
                if success:
                    # Mark as sent
                    delivery.reminder_sms_sent = True
                    delivery.save(update_fields=['reminder_sms_sent'])
                    sent_count += 1
                    logger.info(f"✅ Reminder SMS sent for delivery {delivery.id} to {phone_number}")
                else:
                    failed_count += 1
                    logger.error(f"❌ Failed to send reminder SMS for delivery {delivery.id} to {phone_number}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Error sending reminder SMS for delivery {delivery.id}: {str(e)}", exc_info=True)
        
        result_msg = f"Reminder SMS check completed: {sent_count} sent, {failed_count} failed"
        logger.info(result_msg)
        
        return {
            'success': True,
            'checked': deliveries.count(),
            'sent': sent_count,
            'failed': failed_count,
            'timestamp': now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error in check_and_send_delivery_reminders task: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }

