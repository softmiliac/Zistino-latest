from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Address(models.Model):
    """User address book entries - matches AddressModel fields."""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    plate = models.CharField(max_length=50, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_number = models.CharField(max_length=100, blank=True, null=True)
    vat_number = models.CharField(max_length=100, blank=True, null=True)
    fax = models.CharField(max_length=50, blank=True, null=True, help_text='Fax number')
    website = models.URLField(blank=True, null=True, help_text='Website URL')
    title = models.CharField(max_length=255, blank=True, null=True, help_text='Address title/label')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'addresses'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class Vehicle(models.Model):
    """Driver vehicle profile - matches VehicleRqm fields."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    model_make = models.CharField(max_length=255, blank=True)
    plate_num = models.CharField(max_length=50, blank=True)
    licence = models.CharField(max_length=100, blank=True)
    bodytype = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    registration_num = models.CharField(max_length=100, blank=True)
    engine_size = models.CharField(max_length=50, blank=True)
    tank = models.CharField(max_length=50, blank=True)
    numoftyres = models.CharField(max_length=50, blank=True)
    gps_device_id = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    protocol = models.CharField(max_length=50, blank=True, help_text='GPS device communication protocol (e.g., TCP, UDP, HTTP, HTTPS)')
    port = models.IntegerField(default=0, help_text='Network port number for GPS device communication. 0 = not configured (use default port). Common ports: 80 (HTTP), 443 (HTTPS), 8080 (alternative HTTP), 5027 (TCP), etc.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicles'
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'

    def __str__(self):
        return f"{self.model_make} {self.plate_num}"


class Zone(models.Model):
    """Zone model for geographic areas - matches ZoneModel."""
    id = models.AutoField(primary_key=True)
    zone = models.CharField(max_length=255)
    zonepath = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text='Zone center point latitude')
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text='Zone center point longitude')
    radius_km = models.DecimalField(max_digits=10, decimal_places=2, default=10.0, help_text='Zone radius in kilometers')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'zones'
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'

    def __str__(self):
        return f"{self.zone}"
    
    def calculate_distance_km(self, lat, lng):
        """
        Calculate distance from zone center to given coordinates using Haversine formula.
        Returns distance in kilometers.
        """
        if not self.center_latitude or not self.center_longitude:
            return None
        
        from math import radians, cos, sin, asin, sqrt
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1 = radians(float(self.center_latitude)), radians(float(self.center_longitude))
        lat2, lon2 = radians(float(lat)), radians(float(lng))
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        distance = c * r
        
        return distance
    
    def contains_point(self, lat, lng):
        """Check if a point (lat, lng) is within this zone's radius."""
        if not self.center_latitude or not self.center_longitude:
            return False
        
        distance = self.calculate_distance_km(lat, lng)
        if distance is None:
            return False
        
        return distance <= float(self.radius_km)


class UserZone(models.Model):
    """Junction model linking users to zones - matches UserZoneModel."""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_zones')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='user_zones')
    last_modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_zones'
        verbose_name = 'User Zone'
        verbose_name_plural = 'User Zones'
        unique_together = ('user', 'zone')
        indexes = [
            models.Index(fields=['zone']),
        ]

    def __str__(self):
        return f"{self.user.phone_number} - {self.zone.zone}"