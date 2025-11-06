# from django.db import models
# from myapp.model.locations_model import Location
# from myapp.model.birthday_party_packages_model import BirthdayPartyPackage
# from myapp.model.party_balloon_Packages import PartyBalloonPackage

# class BirthdayBalloonPackageAssociation(models.Model):
#     birthday_party_balloon_id = models.AutoField(primary_key=True)
#     location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='birthday_party_balloon_packages')
#     birthday_party_package = models.ForeignKey(BirthdayPartyPackage, on_delete=models.CASCADE, related_name='balloon_associations')
#     party_balloon_package = models.ForeignKey(PartyBalloonPackage, on_delete=models.CASCADE, related_name='birthday_associations')
    
#     # New required fields
#     code = models.CharField(max_length=50, blank=False, null=False, unique=True)
#     credit = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
#     discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
#     # Optional fields
#     note = models.TextField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         db_table = 'birthday_party_balloon_packages'
#         ordering = ['birthday_party_package', 'party_balloon_package']
#         unique_together = ['birthday_party_package', 'party_balloon_package']
        
#     def __str__(self):
#         return f"{self.birthday_party_package.package_name} - {self.party_balloon_package.package_name}"

#     @property
#     def final_price(self):
#         """Calculate final price after discount"""
#         balloon_price = self.party_balloon_package.price
#         if self.discount:
#             return balloon_price - self.discount
#         return balloon_price






from django.db import models
from myapp.model.locations_model import Location
from myapp.model.birthday_party_packages_model import BirthdayPartyPackage
from myapp.model.party_balloon_Packages import PartyBalloonPackage

class BirthdayBalloonPackageAssociation(models.Model):
    birthday_party_balloon_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='birthday_party_balloon_packages')
    birthday_party_package = models.ForeignKey(BirthdayPartyPackage, on_delete=models.CASCADE, related_name='balloon_associations')
    party_balloon_package = models.ForeignKey(PartyBalloonPackage, on_delete=models.CASCADE, related_name='birthday_associations')
    
    # Required fields
    code = models.CharField(max_length=50, blank=False, null=False, unique=True)
    credit = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Optional fields
    note = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'birthday_party_balloon_associations'   # ✅ changed here
        ordering = ['birthday_party_package', 'party_balloon_package']
        unique_together = ['birthday_party_package', 'party_balloon_package']
        
    def __str__(self):
        return f"{self.birthday_party_package.package_name} - {self.party_balloon_package.package_name}"

    @property
    def final_price(self):
        """Calculate final price after discount"""
        balloon_price = self.party_balloon_package.price
        if self.discount:
            return balloon_price - self.discount
        return balloon_price




# CREATE TABLE `birthday_party_balloon_associations` (
#   `birthday_party_balloon_id` INT AUTO_INCREMENT PRIMARY KEY,
#   `location_id` INT NOT NULL,
#   `birthday_party_package_id` INT NOT NULL,
#   `party_balloon_package_id` INT NOT NULL,
#   `code` VARCHAR(50) NOT NULL UNIQUE,
#   `credit` DECIMAL(10,2) NOT NULL,
#   `discount` DECIMAL(10,2) DEFAULT NULL,
#   `note` TEXT DEFAULT NULL,
#   `is_active` BOOLEAN DEFAULT TRUE,
#   `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
#   `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),

#   UNIQUE KEY `unique_birthday_party_balloon` (`birthday_party_package_id`, `party_balloon_package_id`),

#   CONSTRAINT `fk_birthday_balloon_location`
#     FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`)
#     ON DELETE CASCADE,

#   CONSTRAINT `fk_birthday_balloon_birthday_package`
#     FOREIGN KEY (`birthday_party_package_id`) REFERENCES `birthday_party_packages` (`birthday_party_packages_id`)
#     ON DELETE CASCADE,

#   CONSTRAINT `fk_birthday_balloon_party_package`
#     FOREIGN KEY (`party_balloon_package_id`) REFERENCES `party_balloon_packages` (`party_balloon_package_id`)
#     ON DELETE CASCADE
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;







# CREATE TABLE `birthday_party_balloon_associations` (
#   `birthday_party_balloon_id` INT AUTO_INCREMENT PRIMARY KEY,
#   `location_id` INT NOT NULL,
#   `birthday_party_package_id` INT NOT NULL,
#   `party_balloon_package_id` INT NOT NULL,
#   `code` VARCHAR(50) NOT NULL UNIQUE,
#   `credit` DECIMAL(10,2) NOT NULL,
#   `discount` DECIMAL(10,2) DEFAULT NULL,
#   `note` TEXT DEFAULT NULL,
#   `is_active` BOOLEAN DEFAULT TRUE,
#   `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
#   `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),

#   UNIQUE KEY `unique_birthday_party_balloon` (`birthday_party_package_id`, `party_balloon_package_id`),

#   CONSTRAINT `fk_birthday_balloon_location`
#     FOREIGN KEY (`location_id`) REFERENCES `myapp_locations` (`location_id`)
#     ON DELETE CASCADE,

#   CONSTRAINT `fk_birthday_balloon_birthday_package`
#     FOREIGN KEY (`birthday_party_package_id`) REFERENCES `birthday_party_packages` (`birthday_party_packages_id`)
#     ON DELETE CASCADE,

#   CONSTRAINT `fk_birthday_balloon_party_package`
#     FOREIGN KEY (`party_balloon_package_id`) REFERENCES `party_balloon_packages` (`party_balloon_package_id`)
#     ON DELETE CASCADE
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

