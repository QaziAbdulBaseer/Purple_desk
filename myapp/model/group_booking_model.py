from django.db import models
from myapp.model.locations_model import Location

class GroupBooking(models.Model):
    group_booking_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='group_bookings')
    group_packages = models.CharField(max_length=255, blank=False, null=False)
    call_flow_priority = models.IntegerField()
    flat_fee_jumper_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_jumpers = models.IntegerField()
    instruction = models.TextField(blank=True, null=True)
    package_inclusions = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'group_booking'
        ordering = ['call_flow_priority']
        unique_together = ['location', 'group_packages']
        
    def __str__(self):
        return f"{self.group_packages} - {self.location.location_name}"