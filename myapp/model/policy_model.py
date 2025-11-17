from django.db import models
from myapp.model.locations_model import Location

class Policy(models.Model):
    policy_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='policies')
    policy_type = models.CharField(max_length=255, blank=False, null=False)
    details = models.TextField(blank=False, null=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'policies'
        ordering = ['policy_id']
        unique_together = ['location', 'policy_type']
        
    def __str__(self):
        return f"{self.policy_type} - {self.location.location_name}"