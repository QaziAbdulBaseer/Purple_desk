# #  Ok now i want to add few more coloums in the Location table 

# # I want to add all that coloums = 
# # minimum_jumpers_party
# # guest_of_honor_included_in_minimum_jumpers_party
# # add_additional_hour_of_jump_instruction
# # add_additional_half_hour_of_jump_instruction
# # party_booking_allowed_days_before_party_date
# # party_reschedule_allowed_before_party_date_days
# # add_shirts_while_booking
# # elite_member_party_discount_percentage
# # membership_cancellation_days
# # timezone
# # location_name
# # address
# # address_map_link
# # little_leaper_age_bracket
# # glow_age_bracket
# # twilio_number
# # transfer_number
# # from_email_address
# # minimum_deposit_required_for_booking
# # pitch_ballons_while_booking
# # is_booking_bot
# # is_edit_bot
# # pitch_group_rates
# # pitch_rental_facility
# # additional_jumper_discount
# # add_party_space_sentence


# # but few coloum are already exist so leave that as they are.

# # remember you donot have to change any existing then for the (table the colum that already there leave them as it is)


# # and the value is = = = 


# # variable_name	value
# # minimum_jumpers_party	10
# # guest_of_honor_included_in_minimum_jumpers_party	no
# # add_additional_hour_of_jump_instruction	no
# # add_additional_half_hour_of_jump_instruction	no
# # party_booking_allowed_days_before_party_date	3
# # party_reschedule_allowed_before_party_date_days	3
# # add_shirts_while_booking	no
# # elite_member_party_discount_percentage	20
# # membership_cancellation_days	3
# # timezone	America/Chicago
# # location_name	Biloxi
# # address	Edgewater Dr, Biloxi, Mississippi, three nine five three one
# # address_map_link	https://maps.app.goo.gl/gzJ3ETazorgffAJs6
# # little_leaper_age_bracket	Recommended for Kids of age 6 years old and under 
# # glow_age_bracket	Recommended for Kids of 3 years old and above
# # twilio_number	18788778230
# # transfer_number	923318592344
# # from_email_address	shereen@purpledesk.ai
# # minimum_deposit_required_for_booking	50 percent
# # pitch_ballons_while_booking	no
# # is_booking_bot	no
# # is_edit_bot	no
# # pitch_group_rates	yes
# # pitch_rental_facility	yes
# # additional_jumper_discount	no
# # add_party_space_sentence	no

# from django.db import models

# # Create your models here.


# class Location(models.Model):
#     location_id = models.AutoField(primary_key=True)
#     location_name = models.CharField(max_length=255, unique=True)
#     location_address = models.TextField()
#     location_timezone = models.CharField(max_length=100)
#     location_call_number = models.CharField(max_length=20, blank=True, null=True)
#     location_transfer_number = models.CharField(max_length=20, blank=True, null=True)
#     location_google_map_link = models.URLField(max_length=500, blank=True, null=True)

#     def _str_(self):
#         return self.location_name






from django.db import models

class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=255, unique=True)
    location_address = models.TextField()
    location_timezone = models.CharField(max_length=100)
    location_call_number = models.CharField(max_length=20, blank=True, null=True)
    location_transfer_number = models.CharField(max_length=20, blank=True, null=True)
    location_google_map_link = models.URLField(max_length=500, blank=True, null=True)
    
    # New fields
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
    minimum_deposit_required_for_booking = models.CharField(max_length=50, default='50 percent')
    pitch_ballons_while_booking = models.BooleanField(default=False)
    is_booking_bot = models.BooleanField(default=False)
    is_edit_bot = models.BooleanField(default=False)
    pitch_group_rates = models.BooleanField(default=True)
    pitch_rental_facility = models.BooleanField(default=True)
    additional_jumper_discount = models.BooleanField(default=False)
    add_party_space_sentence = models.BooleanField(default=False)

    def __str__(self):
        return self.location_name