from django.db import models
from myapp.model.locations_model import Location


class JumpPass(models.Model):
    jump_pass_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='jump_passes')
    
    # Required fields
    jump_pass_priority = models.IntegerField()
    schedule_with = models.CharField(max_length=255)
    pass_name = models.CharField(max_length=255, blank=False, null=False)
    age_allowed = models.CharField(max_length=255)
    jump_time_allowed = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_included = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Tax percentage (e.g., 10.00 for 10%)")
    recommendation = models.TextField()
    
    # Optional fields
    jump_pass_pitch = models.TextField(blank=True, null=True)
    starting_day_name = models.CharField(max_length=50, blank=True, null=True)
    ending_day_name = models.CharField(max_length=50, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jump_passes'
        ordering = ['jump_pass_priority']
        
    def __str__(self):
        return f"{self.pass_name} - {self.location.location_name}"