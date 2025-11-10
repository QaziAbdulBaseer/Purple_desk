from django.db import models
from myapp.model.locations_model import Location


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
    tax_included = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Tax percentage (e.g., 10.00 for 10%)")
    birthday_party_booking_lead_allowed_days = models.IntegerField()
    birthday_party_reschedule_allowed_days = models.IntegerField()
    each_additional_jumper_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    
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