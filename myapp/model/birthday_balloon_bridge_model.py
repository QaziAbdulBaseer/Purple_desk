

from django.db import models
from myapp.model.birthday_party_packages_model import BirthdayPartyPackage
from myapp.model.balloon_party_packages_model import BalloonPartyPackage

class BirthdayBalloonBridge(models.Model):
    birthday_balloon_bridge_id = models.AutoField(primary_key=True)
    birthday_party_package = models.ForeignKey(
        BirthdayPartyPackage, 
        on_delete=models.CASCADE, 
        related_name='balloon_packages_bridge',
        db_column='birthday_party_packages_id'
    )
    balloon_party_package = models.ForeignKey(
        BalloonPartyPackage, 
        on_delete=models.CASCADE, 
        related_name='birthday_packages_bridge',
        db_column='balloon_party_packages_id'
    )
    
    # Additional fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'birthday_balloon_bridge'
        unique_together = ('birthday_party_package', 'balloon_party_package')
        
    def __str__(self):
        return f"{self.birthday_party_package.package_name} - {self.balloon_party_package.package_name}"