"""
Utility functions for driver assignment and zone detection.
"""
from zistino_apps.users.models import Zone, UserZone
from django.contrib.auth import get_user_model
from zistino_apps.deliveries.models import Delivery
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()


def find_zone_for_location(latitude, longitude):
    """
    Find the zone that contains the given latitude/longitude coordinates.
    Returns the Zone object or None if no zone found.
    
    Uses distance-based matching: finds the closest zone within its radius.
    If multiple zones contain the point, returns the closest one.
    """
    if not latitude or not longitude:
        return None
    
    # Find all active zones
    zones = Zone.objects.filter(is_active=True, center_latitude__isnull=False, center_longitude__isnull=False)
    
    # Find zones that contain this point
    containing_zones = []
    for zone in zones:
        if zone.contains_point(latitude, longitude):
            distance = zone.calculate_distance_km(latitude, longitude)
            containing_zones.append((zone, distance))
    
    if not containing_zones:
        # If no zone contains the point, find the nearest zone
        min_distance = float('inf')
        nearest_zone = None
        for zone in zones:
            distance = zone.calculate_distance_km(latitude, longitude)
            if distance is not None and distance < min_distance:
                min_distance = distance
                nearest_zone = zone
        return nearest_zone
    
    # Return the closest zone that contains the point
    containing_zones.sort(key=lambda x: x[1])
    return containing_zones[0][0]


def assign_driver_to_order(order, zone):
    """
    Automatically assign a driver from the given zone to the order.
    Uses round-robin strategy: assigns to driver with least pending deliveries.
    
    Returns the created Delivery object or None if no driver found.
    """
    if not zone:
        return None
    
    # Find all active drivers in this zone
    user_zones = UserZone.objects.filter(
        zone=zone,
        user__is_driver=True,
        user__is_active=True,
        user__is_active_driver=True
    ).select_related('user')
    
    if not user_zones.exists():
        return None
    
    # Get driver IDs
    driver_ids = [uz.user.id for uz in user_zones]
    
    # Find driver with least pending/assigned deliveries (round-robin / least loaded)
    drivers_with_counts = []
    for driver_id in driver_ids:
        pending_count = Delivery.objects.filter(
            driver_id=driver_id,
            status__in=['assigned', 'in_progress']
        ).count()
        drivers_with_counts.append((driver_id, pending_count))
    
    # Sort by pending count (ascending) - least loaded first
    drivers_with_counts.sort(key=lambda x: x[1])
    selected_driver_id = drivers_with_counts[0][0]
    
    # Get the selected driver
    selected_driver = User.objects.get(id=selected_driver_id)
    
    # Create delivery
    delivery = Delivery.objects.create(
        driver=selected_driver,
        order=order,
        status='assigned',
        address=order.address1 or order.address2 or '',
        phone_number=order.phone1 or order.phone2 or order.user_phone_number or '',
        latitude=order.latitude,
        longitude=order.longitude,
    )
    
    return delivery


def find_nearest_time_slot(requested_date=None):
    """
    Find the nearest available time slot for delivery.
    
    If customer registers during a time slot (e.g., 10 AM in 8 AM - 12 PM slot),
    automatically selects the next available slot (e.g., 12 PM - 4 PM).
    
    Args:
        requested_date: Optional datetime for the requested delivery date.
                        If None, uses today.
    
    Returns:
        Tuple of (datetime, time_slot_info) where datetime is the selected delivery date/time,
        and time_slot_info is a dict with 'start_hour', 'end_hour', 'formatted'.
        Returns None if no configuration found.
    """
    try:
        from zistino_apps.configurations.models import Configuration
        
        # Get delivery time configuration
        config = Configuration.objects.filter(
            name__icontains='delivery_time',
            is_active=True
        ).first()
        
        if not config or not config.value:
            # Fallback to defaults
            start_hour = 8
            end_hour = 20
            split = 4
        else:
            start_hour = int(config.value.get('start', 8))
            end_hour = int(config.value.get('end', 20))
            split = int(config.value.get('split', 4))
    except Exception:
        # Fallback to defaults if any error
        start_hour = 8
        end_hour = 20
        split = 4
    
    now = timezone.now()
    
    # Use requested_date if provided, otherwise use today or tomorrow
    if requested_date:
        target_date = requested_date
    else:
        target_date = now
    
    # Generate time slots
    slots = []
    current = start_hour
    while current < end_hour:
        slot_end = min(current + split, end_hour)
        slots.append((current, slot_end))
        current = slot_end
    
    # Find current hour
    current_hour = now.hour
    
    # Find the nearest available slot
    # If current time is within a slot, select the next slot
    # Otherwise, select the next available slot from now
    
    selected_slot = None
    selected_date = target_date
    
    for slot_start, slot_end in slots:
        # If current hour is within this slot, select the next slot
        if slot_start <= current_hour < slot_end:
            # Find next slot
            slot_index = slots.index((slot_start, slot_end))
            if slot_index + 1 < len(slots):
                selected_slot = slots[slot_index + 1]
            else:
                # No more slots today, use first slot tomorrow
                selected_slot = slots[0]
                selected_date = now + timedelta(days=1)
            break
        # If current hour is before this slot, select this slot
        elif current_hour < slot_start:
            selected_slot = (slot_start, slot_end)
            break
    
    # If no slot found (current hour is after all slots), use first slot tomorrow
    if not selected_slot:
        selected_slot = slots[0]
        selected_date = now + timedelta(days=1)
    
    # Create delivery datetime (use start of the selected slot)
    delivery_datetime = selected_date.replace(
        hour=selected_slot[0],
        minute=0,
        second=0,
        microsecond=0
    )
    
    # Format time slot
    def format_hour(h):
        if h == 0:
            return "12 AM"
        elif h < 12:
            return f"{h} AM"
        elif h == 12:
            return "12 PM"
        else:
            return f"{h - 12} PM"
    
    time_slot_info = {
        'start_hour': selected_slot[0],
        'end_hour': selected_slot[1],
        'formatted': f"{format_hour(selected_slot[0])} to {format_hour(selected_slot[1])}"
    }
    
    return delivery_datetime, time_slot_info

