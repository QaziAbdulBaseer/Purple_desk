

# # hi i want to update the Birthday party package. table. 
# # and also want to update its views and serializers
# # so you see and tell me which part i what to update. and its better to give a compleate function that i replace

# # ok now i donot need = =  Booking Lead Days * and  Reschedule Days *  

# # and now i need new coloum like = = = party_environment_name , food_included_count	drinks_included_count , pearks_for_Guest_of_honor


# from django.db import models
# from myapp.model.locations_model import Location
# from myapp.model.balloon_party_packages_model import BalloonPartyPackage

# class BirthdayPartyPackage(models.Model):
#     birthday_party_packages_id = models.AutoField(primary_key=True)
#     location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='birthday_party_packages')
#     package_name = models.CharField(max_length=255, blank=False, null=False)
#     birthday_party_priority = models.IntegerField()
#     availability_days = models.CharField(max_length=255)
#     schedule_with = models.CharField(max_length=255)
#     minimum_jumpers = models.IntegerField()
#     jump_time = models.CharField(max_length=255)
#     party_room_time = models.CharField(max_length=255)
#     food_and_drinks = models.CharField(max_length=500)
#     paper_goods = models.CharField(max_length=255)
#     skysocks = models.CharField(max_length=255)
#     dessert_policy = models.CharField(max_length=255)
#     other_perks = models.CharField(max_length=500)
#     outside_food_drinks_fee = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     guest_of_honour_included_in_total_jumpers = models.BooleanField(default=False)
#     tax_included = models.BooleanField(default=True)
#     birthday_party_booking_lead_allowed_days = models.IntegerField()
#     birthday_party_reschedule_allowed_days = models.IntegerField()
#     each_additional_jumper_price = models.DecimalField(max_digits=10, decimal_places=2)
#     is_available = models.BooleanField(default=True)
    
#     # New fields for balloon package
#     balloon_package_included = models.BooleanField(default=False)
#     promotion_code = models.CharField(max_length=50, blank=True, null=True)
#     credit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     balloon_party_package = models.ForeignKey(
#         BalloonPartyPackage, 
#         on_delete=models.SET_NULL, 
#         blank=True, 
#         null=True,
#         related_name='birthday_party_packages'
#     )
    
#     # NEW FIELD: is_any_balloon_package_is_free
#     is_any_balloon_package_is_free = models.BooleanField(default=False)
    
#     # Optional fields
#     birthday_party_pitch = models.TextField(blank=True, null=True)
#     Is_additional_jumpers_allowed = models.BooleanField(default=True)
#     each_additional_jump_hour_after_room_time = models.CharField(max_length=255, blank=True, null=True)
#     additional_instructions = models.TextField(blank=True, null=True)
#     birthday_party_discount_code = models.CharField(max_length=50, blank=True, null=True)
#     birthday_party_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
#     roller_birthday_party_search_id = models.CharField(max_length=255, blank=True, null=True)
#     roller_additional_jumper_price_search_id = models.CharField(max_length=255, blank=True, null=True)
#     roller_birthday_party_booking_id = models.CharField(max_length=255, blank=True, null=True)
#     each_additional_jump_half_hour_after_room_time = models.CharField(max_length=255, blank=True, null=True)
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         db_table = 'birthday_party_packages'
#         ordering = ['birthday_party_priority']
        
#     def __str__(self):
#         return f"{self.package_name} - {self.location.location_name}"










from django.db import models
from myapp.model.locations_model import Location
from myapp.model.balloon_party_packages_model import BalloonPartyPackage

class BirthdayPartyPackage(models.Model):
    birthday_party_packages_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='birthday_party_packages')
    package_name = models.CharField(max_length=255, blank=False, null=False)
    birthday_party_priority = models.IntegerField()
    availability_days = models.CharField(max_length=255)
    schedule_with = models.CharField(max_length=255)
    minimum_jumpers = models.IntegerField()
    jump_time = models.CharField(max_length=255)
    party_room_time = models.CharField(max_length=255)
    food_and_drinks = models.CharField(max_length=500)
    paper_goods = models.CharField(max_length=255)
    skysocks = models.CharField(max_length=255)
    dessert_policy = models.CharField(max_length=255)
    other_perks = models.CharField(max_length=500)
    outside_food_drinks_fee = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    guest_of_honour_included_in_total_jumpers = models.BooleanField(default=False)
    tax_included = models.BooleanField(default=True)
    # REMOVED: birthday_party_booking_lead_allowed_days
    # REMOVED: birthday_party_reschedule_allowed_days
    each_additional_jumper_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    
    # New fields for balloon package
    balloon_package_included = models.BooleanField(default=False)
    promotion_code = models.CharField(max_length=50, blank=True, null=True)
    credit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    balloon_party_package = models.ForeignKey(
        BalloonPartyPackage, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='birthday_party_packages'
    )
    
    # NEW FIELD: is_any_balloon_package_is_free
    is_any_balloon_package_is_free = models.BooleanField(default=False)
    
    # NEW FIELDS: Added as requested
    party_environment_name = models.CharField(max_length=255, blank=True, null=True)
    food_included_count = models.IntegerField(blank=True, null=True)
    drinks_included_count = models.IntegerField(blank=True, null=True)
    perks_for_guest_of_honor = models.TextField(blank=True, null=True)
    
    # Optional fields
    birthday_party_pitch = models.TextField(blank=True, null=True)
    Is_additional_jumpers_allowed = models.BooleanField(default=True)
    each_additional_jump_hour_after_room_time = models.CharField(max_length=255, blank=True, null=True)
    additional_instructions = models.TextField(blank=True, null=True)
    birthday_party_discount_code = models.CharField(max_length=50, blank=True, null=True)
    birthday_party_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    roller_birthday_party_search_id = models.CharField(max_length=255, blank=True, null=True)
    roller_additional_jumper_price_search_id = models.CharField(max_length=255, blank=True, null=True)
    roller_birthday_party_booking_id = models.CharField(max_length=255, blank=True, null=True)
    each_additional_jump_half_hour_after_room_time = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'birthday_party_packages'
        ordering = ['birthday_party_priority']
        
    def __str__(self):
        return f"{self.package_name} - {self.location.location_name}"