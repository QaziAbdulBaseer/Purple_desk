



# # # CREATE TABLE myapp_location (
# # #     location_id SERIAL PRIMARY KEY,
# # #     location_name VARCHAR(255) UNIQUE NOT NULL,
# # #     location_address TEXT NOT NULL,
# # #     location_timezone VARCHAR(100) NOT NULL,
# # #     location_call_number VARCHAR(20),
# # #     location_transfer_number VARCHAR(20),
# # #     location_google_map_link VARCHAR(500),

# # #     minimum_jumpers_party INTEGER NOT NULL DEFAULT 10,
# # #     guest_of_honor_included_in_minimum_jumpers_party BOOLEAN NOT NULL DEFAULT FALSE,
# # #     add_additional_hour_of_jump_instruction BOOLEAN NOT NULL DEFAULT FALSE,
# # #     add_additional_half_hour_of_jump_instruction BOOLEAN NOT NULL DEFAULT FALSE,
# # #     party_booking_allowed_days_before_party_date INTEGER NOT NULL DEFAULT 3,
# # #     party_reschedule_allowed_before_party_date_days INTEGER NOT NULL DEFAULT 3,
# # #     add_shirts_while_booking BOOLEAN NOT NULL DEFAULT FALSE,
# # #     elite_member_party_discount_percentage INTEGER NOT NULL DEFAULT 20,
# # #     membership_cancellation_days INTEGER NOT NULL DEFAULT 3,
# # #     little_leaper_age_bracket VARCHAR(255) NOT NULL DEFAULT 'Recommended for Kids of age 6 years old and under',
# # #     glow_age_bracket VARCHAR(255) NOT NULL DEFAULT 'Recommended for Kids of 3 years old and above',
# # #     from_email_address VARCHAR(254) NOT NULL DEFAULT 'shereen@purpledesk.ai',
# # #     minimum_deposit_required_for_booking VARCHAR(50) NOT NULL DEFAULT '50 percents',
# # #     pitch_ballons_while_booking BOOLEAN NOT NULL DEFAULT FALSE,
# # #     is_booking_bot BOOLEAN NOT NULL DEFAULT FALSE,
# # #     is_edit_bot BOOLEAN NOT NULL DEFAULT FALSE,
# # #     pitch_group_rates BOOLEAN NOT NULL DEFAULT TRUE,
# # #     pitch_rental_facility BOOLEAN NOT NULL DEFAULT TRUE,
# # #     additional_jumper_discount BOOLEAN NOT NULL DEFAULT FALSE,
# # #     add_party_space_sentence BOOLEAN NOT NULL DEFAULT FALSE
# # # );


# # from django.db import models

# # class Location(models.Model):
# #     location_id = models.AutoField(primary_key=True)
# #     location_name = models.CharField(max_length=255, unique=True)
# #     location_address = models.TextField()
# #     location_timezone = models.CharField(max_length=100)
# #     location_call_number = models.CharField(max_length=20, blank=True, null=True)
# #     location_transfer_number = models.CharField(max_length=20, blank=True, null=True)
# #     location_google_map_link = models.URLField(max_length=500, blank=True, null=True)
    
# #     # New fields
# #     minimum_jumpers_party = models.IntegerField(default=10)
# #     guest_of_honor_included_in_minimum_jumpers_party = models.BooleanField(default=False)
# #     add_additional_hour_of_jump_instruction = models.BooleanField(default=False)
# #     add_additional_half_hour_of_jump_instruction = models.BooleanField(default=False)
# #     party_booking_allowed_days_before_party_date = models.IntegerField(default=3)
# #     party_reschedule_allowed_before_party_date_days = models.IntegerField(default=3)
# #     add_shirts_while_booking = models.BooleanField(default=False)
# #     elite_member_party_discount_percentage = models.IntegerField(default=20)
# #     membership_cancellation_days = models.IntegerField(default=3)
# #     little_leaper_age_bracket = models.CharField(max_length=255, default='Recommended for Kids of age 6 years old and under')
# #     glow_age_bracket = models.CharField(max_length=255, default='Recommended for Kids of 3 years old and above')
# #     from_email_address = models.EmailField(default='shereen@purpledesk.ai')
# #     minimum_deposit_required_for_booking = models.CharField(max_length=50, default='50 percents')
# #     pitch_ballons_while_booking = models.BooleanField(default=False)
# #     is_booking_bot = models.BooleanField(default=False)
# #     is_edit_bot = models.BooleanField(default=False)
# #     pitch_group_rates = models.BooleanField(default=True)
# #     pitch_rental_facility = models.BooleanField(default=True)
# #     additional_jumper_discount = models.BooleanField(default=False)
# #     add_party_space_sentence = models.BooleanField(default=False)

# #     def __str__(self):
# #         return self.location_name








# # # models.py
# # from django.db import models
# # from django.utils import timezone

# # class Location(models.Model):
# #     location_id = models.AutoField(primary_key=True)
# #     location_name = models.CharField(max_length=255, unique=True)
# #     location_address = models.TextField()
# #     location_timezone = models.CharField(max_length=100)
# #     location_call_number = models.CharField(max_length=20, blank=True, null=True)
# #     location_transfer_number = models.CharField(max_length=20, blank=True, null=True)
# #     location_google_map_link = models.URLField(max_length=500, blank=True, null=True)
    
# #     # Roller API fields
# #     roller_client_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Roller Client ID")
# #     roller_client_secret = models.CharField(max_length=255, blank=True, null=True, verbose_name="Roller Client Secret")
# #     roller_access_token = models.TextField(blank=True, null=True, verbose_name="Roller Access Token")
# #     roller_token_created_at = models.DateTimeField(blank=True, null=True, verbose_name="Token Created At")
    
# #     # Existing fields
# #     minimum_jumpers_party = models.IntegerField(default=10)
# #     guest_of_honor_included_in_minimum_jumpers_party = models.BooleanField(default=False)
# #     add_additional_hour_of_jump_instruction = models.BooleanField(default=False)
# #     add_additional_half_hour_of_jump_instruction = models.BooleanField(default=False)
# #     party_booking_allowed_days_before_party_date = models.IntegerField(default=3)
# #     party_reschedule_allowed_before_party_date_days = models.IntegerField(default=3)
# #     add_shirts_while_booking = models.BooleanField(default=False)
# #     elite_member_party_discount_percentage = models.IntegerField(default=20)
# #     membership_cancellation_days = models.IntegerField(default=3)
# #     little_leaper_age_bracket = models.CharField(max_length=255, default='Recommended for Kids of age 6 years old and under')
# #     glow_age_bracket = models.CharField(max_length=255, default='Recommended for Kids of 3 years old and above')
# #     from_email_address = models.EmailField(default='shereen@purpledesk.ai')
# #     minimum_deposit_required_for_booking = models.CharField(max_length=50, default='50 percents')
# #     pitch_ballons_while_booking = models.BooleanField(default=False)
# #     is_booking_bot = models.BooleanField(default=False)
# #     is_edit_bot = models.BooleanField(default=False)
# #     pitch_group_rates = models.BooleanField(default=True)
# #     pitch_rental_facility = models.BooleanField(default=True)
# #     additional_jumper_discount = models.BooleanField(default=False)
# #     add_party_space_sentence = models.BooleanField(default=False)

# #     def is_token_expired(self):
# #         """Check if token is older than 23 hours"""
# #         if not self.roller_token_created_at or not self.roller_access_token:
# #             return True
# #         time_difference = timezone.now() - self.roller_token_created_at
# #         return time_difference.total_seconds() > (23 * 3600)  # 23 hours in seconds

# #     def __str__(self):
# #         return self.location_name

# #     class Meta:
# #         verbose_name = "Location"
# #         verbose_name_plural = "Locations"







# from django.db import models
# from django.utils import timezone

# class Location(models.Model):
#     location_id = models.AutoField(primary_key=True)
#     location_name = models.CharField(max_length=255, unique=True)
#     location_address = models.TextField()
#     location_timezone = models.CharField(max_length=100)
#     location_call_number = models.CharField(max_length=20, blank=True, null=True)
#     location_transfer_number = models.CharField(max_length=20, blank=True, null=True)
#     location_google_map_link = models.URLField(max_length=500, blank=True, null=True)
    
#     # --- ADD THESE 4 NEW FIELDS ---
#     roller_client_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Roller Client ID")
#     roller_client_secret = models.CharField(max_length=255, blank=True, null=True, verbose_name="Roller Client Secret")
#     roller_access_token = models.TextField(blank=True, null=True, verbose_name="Roller Access Token")
#     roller_token_created_at = models.DateTimeField(blank=True, null=True, verbose_name="Token Created At")
#     # --- END OF NEW FIELDS ---
    
#     # Existing fields
#     minimum_jumpers_party = models.IntegerField(default=10)
#     guest_of_honor_included_in_minimum_jumpers_party = models.BooleanField(default=False)
#     add_additional_hour_of_jump_instruction = models.BooleanField(default=False)
#     add_additional_half_hour_of_jump_instruction = models.BooleanField(default=False)
#     party_booking_allowed_days_before_party_date = models.IntegerField(default=3)
#     party_reschedule_allowed_before_party_date_days = models.IntegerField(default=3)
#     add_shirts_while_booking = models.BooleanField(default=False)
#     elite_member_party_discount_percentage = models.IntegerField(default=20)
#     membership_cancellation_days = models.IntegerField(default=3)
#     little_leaper_age_bracket = models.CharField(max_length=255, default='Recommended for Kids of age 6 years old and under')
#     glow_age_bracket = models.CharField(max_length=255, default='Recommended for Kids of 3 years old and above')
#     from_email_address = models.EmailField(default='shereen@purpledesk.ai')
#     minimum_deposit_required_for_booking = models.CharField(max_length=50, default='50 percents')
#     pitch_ballons_while_booking = models.BooleanField(default=False)
#     is_booking_bot = models.BooleanField(default=False)
#     is_edit_bot = models.BooleanField(default=False)
#     pitch_group_rates = models.BooleanField(default=True)
#     pitch_rental_facility = models.BooleanField(default=True)
#     additional_jumper_discount = models.BooleanField(default=False)
#     add_party_space_sentence = models.BooleanField(default=False)

#     def is_token_expired(self):
#         """Check if token is older than 23 hours"""
#         if not self.roller_token_created_at or not self.roller_access_token:
#             return True
#         time_difference = timezone.now() - self.roller_token_created_at
#         return time_difference.total_seconds() > (23 * 3600)  # 23 hours in seconds

#     def __str__(self):
#         return self.location_name

#     class Meta:
#         verbose_name = "Location"
#         verbose_name_plural = "Locations"









from django.db import models
from django.utils import timezone

class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=255, unique=True)
    location_address = models.TextField()
    location_timezone = models.CharField(max_length=100)
    location_call_number = models.CharField(max_length=20, blank=True, null=True)
    location_transfer_number = models.CharField(max_length=20, blank=True, null=True)
    location_google_map_link = models.URLField(max_length=500, blank=True, null=True)
    
    # Roller API fields (4 original fields)
    roller_client_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Roller Client ID")
    roller_client_secret = models.CharField(max_length=255, blank=True, null=True, verbose_name="Roller Client Secret")
    roller_access_token = models.TextField(blank=True, null=True, verbose_name="Roller Access Token")
    roller_token_created_at = models.DateTimeField(blank=True, null=True, verbose_name="Token Created At")
    
    # Existing fields
    minimum_jumpers_party = models.IntegerField(default=10)
    guest_of_honor_included_in_minimum_jumpers_party = models.BooleanField(default=False)
    add_additional_hour_of_jump_instruction = models.BooleanField(default=False)
    add_additional_half_hour_of_jump_instruction = models.BooleanField(default=False)
    party_booking_allowed_days_before_party_date = models.IntegerField(default=3)
    party_reschedule_allowed_before_party_date_days = models.IntegerField(default=3)
    add_shirts_while_booking = models.BooleanField(default=False)
    elite_member_party_discount_percentage = models.IntegerField(default=20)
    membership_cancellation_days = models.IntegerField(default=3)
    little_leaper_age_bracket = models.CharField(max_length=255, default='Recommended for Kids of age 6 years old and under')
    glow_age_bracket = models.CharField(max_length=255, default='Recommended for Kids of 3 years old and above')
    from_email_address = models.EmailField(default='shereen@purpledesk.ai')
    minimum_deposit_required_for_booking = models.CharField(max_length=50, default='50 percents')
    pitch_ballons_while_booking = models.BooleanField(default=False)
    is_booking_bot = models.BooleanField(default=False)
    is_edit_bot = models.BooleanField(default=False)
    pitch_group_rates = models.BooleanField(default=True)
    pitch_rental_facility = models.BooleanField(default=True)
    additional_jumper_discount = models.BooleanField(default=False)
    add_party_space_sentence = models.BooleanField(default=False)

    def is_token_expired(self):
        """Check if token is older than 23 hours"""
        if not self.roller_token_created_at or not self.roller_access_token:
            return True
        time_difference = timezone.now() - self.roller_token_created_at
        return time_difference.total_seconds() > (22 * 3600)  # 23 hours in seconds

    def __str__(self):
        return self.location_name

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"

