from django.db.models.signals import post_save
from django.dispatch import receiver
from zistino_apps.orders.models import Order
from zistino_apps.points.models import Referral, ReferralCode
from zistino_apps.points.views import award_order_points, award_referral_points
from django.utils import timezone


@receiver(post_save, sender=Order)
def award_points_on_order_completion(sender, instance, created, **kwargs):
    """
    Award points when order is completed (status == 3).
    Also check if this is referred user's first order and award referral points.
    """
    # Only process when order status is completed (assuming 3 = completed)
    # Check status change to avoid duplicate awards
    if instance.status == 3:  # Completed status
        # Award order points (1 point per order)
        try:
            award_order_points(instance.user, instance.id)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to award order points for order {instance.id}: {str(e)}")
        
        # Check if this user has a pending referral (first order completion)
        try:
            referral = Referral.objects.filter(
                referred=instance.user,
                status='pending'
            ).first()
            
            if referral and not referral.referrer_points_awarded:
                # This is the first completed order for referred user
                # Award points to referrer (2 points)
                try:
                    award_referral_points(referral.referrer, referral.referred, referral.id)
                    referral.status = 'completed'
                    referral.referrer_points_awarded = True
                    referral.completed_at = timezone.now()
                    referral.save()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to award referral points for referral {referral.id}: {str(e)}")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to process referral for order {instance.id}: {str(e)}")

