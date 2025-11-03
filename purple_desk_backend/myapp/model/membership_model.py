from django.db import models
from myapp.model.locations_model import Location
from django.db.models import JSONField

class Membership(models.Model):
    membership_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='memberships')
    
    # Required fields
    title = models.CharField(max_length=255, blank=False, null=False , unique=True)
    schedule_with = models.JSONField(default=list, null=False, blank=False)
    pitch_priority = models.IntegerField(null=False, blank=False)
    
    # Optional fields
    pitch_introduction = models.TextField(blank=True, null=True)
    activity_time = models.TextField(blank=True, null=True)
    features = models.TextField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)
    party_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    parent_addon_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    subscription = models.CharField(max_length=255, blank=True, null=True)
    tax_included = models.BooleanField(
        null=False,
        blank=False,
        help_text="Check if tax is included in the price (Yes/No or 1/0)."
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'memberships'
        ordering = ['pitch_priority']
        
    def __str__(self):
        return f"{self.title} - {self.location.location_name}"