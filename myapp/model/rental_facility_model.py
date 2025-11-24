from django.db import models
from myapp.model.locations_model import Location

class RentalFacility(models.Model):
    rental_facility_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='rental_facilities')
    rental_jumper_group = models.CharField(max_length=255, blank=False, null=False)
    call_flow_priority = models.IntegerField()
    per_jumper_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_jumpers = models.IntegerField()
    instruction = models.TextField(blank=True, null=True)
    inclusions = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rental_facility'
        ordering = ['call_flow_priority']
        unique_together = ['location', 'rental_jumper_group']
        
    def __str__(self):
        return f"{self.rental_jumper_group} - {self.location.location_name}"