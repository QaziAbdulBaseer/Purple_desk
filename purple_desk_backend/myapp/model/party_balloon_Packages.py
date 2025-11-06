# from django.db import models
# from myapp.model.locations_model import Location

# class PartyBalloonPackage(models.Model):
#     party_balloon_package_id = models.AutoField(primary_key=True)
#     location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='party_balloon_packages')
    
#     # Required fields
#     package_name = models.CharField(max_length=255, blank=False, null=False)
#     call_flow_priority = models.IntegerField(null=False, blank=False)
#     promotional_pitch = models.TextField(blank=False, null=False)
#     package_inclusions = models.TextField(blank=False, null=False)
#     price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    
#     # Optional fields
#     discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     note = models.TextField(blank=True, null=True)
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         db_table = 'birthday_party_balloon_packages'
#         ordering = ['call_flow_priority']
#         unique_together = ['location', 'package_name']
        
#     def __str__(self):
#         return f"{self.package_name} - {self.location.location_name}"





from django.db import models
from myapp.model.locations_model import Location

class PartyBalloonPackage(models.Model):
    party_balloon_package_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='party_balloon_packages')
    
    # Required fields
    package_name = models.CharField(max_length=255, blank=False, null=False)
    call_flow_priority = models.IntegerField(null=False, blank=False)
    promotional_pitch = models.TextField(blank=False, null=False)
    package_inclusions = models.TextField(blank=False, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    
    # Optional fields
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'party_balloon_packages'   # ✅ unique table name
        ordering = ['call_flow_priority']
        unique_together = ['location', 'package_name']
        
    def __str__(self):
        return f"{self.package_name} - {self.location.location_name}"
