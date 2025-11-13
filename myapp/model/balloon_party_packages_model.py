

from django.db import models
from myapp.model.locations_model import Location

class BalloonPartyPackage(models.Model):
    balloon_party_packages_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='balloon_party_packages')
    package_name = models.CharField(max_length=255, blank=False, null=False)
    call_flow_priority = models.IntegerField()
    promotional_pitch = models.TextField(blank=True, null=True)
    package_inclusions = models.TextField(blank=True, null=True)
    discount = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'balloon_party_packages'
        ordering = ['call_flow_priority']
        
    def __str__(self):
        return f"{self.package_name} - {self.location.location_name}"








#         SELECT * FROM purple_desk_db.balloon_party_packages;

# desc purple_desk_db.balloon_party_packages;

# ALTER TABLE balloon_party_packages
# ADD COLUMN location_id INT NOT NULL;

# ALTER TABLE balloon_party_packages
# ADD CONSTRAINT fk_location
# FOREIGN KEY (location_id) REFERENCES locations(location_id);


# ALTER TABLE balloon_party_packages 
# ADD CONSTRAINT fk_location
# FOREIGN KEY (location_id) REFERENCES myapp_location(location_id);


# ALTER TABLE balloon_party_packages 
# ADD COLUMN location_id INT NOT NULL;



# ALTER TABLE balloon_party_packages
# ADD CONSTRAINT fk_location
# FOREIGN KEY (location_id) REFERENCES locations(location_id);


# ALTER TABLE balloon_party_packages
# MODIFY COLUMN location_id INT NOT NULL;


# ALTER TABLE balloon_party_packages
# DROP FOREIGN KEY fk_location;


# ALTER TABLE balloon_party_packages
# ADD CONSTRAINT fk_location
# FOREIGN KEY (location_id) REFERENCES myapp_location(location_id);