



# from django.db import models

# from myapp.model.customer_details_model import CustomerDetails
# from myapp.model.locations_model import Location


# class RollerBookingDetails(models.Model):
#     booking_id = models.AutoField(primary_key=True)
#     # customer_id = models.CharField(max_length=255, blank=False, null=False) # ITS FOREIGN KEY
#     customer = models.ForeignKey(
#         CustomerDetails, 
#         on_delete=models.CASCADE,
#         related_name='bookings',
#         null=False,  # Making it non-nullable since you said it's required
#         help_text="Foreign key to CustomerDetails table"
#     )
#     # location_id = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='booking_location')
#     roller_id = models.CharField(max_length=50, blank=False, null=False)
#     booking_unique_id = models.CharField(max_length=255, blank=True, null=True)
#     booking_date = models.CharField(max_length=255,blank=True, null=True)
#     booking_time = models.CharField(max_length=255, blank=True, null=True)
#     # capacity_reservation_id = models.CharField(max_length=255, blank=True, null=True) # we donot need this 
#     payment_made = models.BooleanField(default=False)
#     deposite_made  = models.FloatField(blank=True, null=True)
#     payload = models.JSONField(blank=True, null=True)
#     creation_date = models.DateTimeField(auto_now=True)
    

        
#     def __str__(self):
#         return f"{self.roller_booking_id}"



from django.db import models
from myapp.model.customer_details_model import CustomerDetails
from myapp.model.locations_model import Location

class RollerBookingDetails(models.Model):
    booking_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(
        CustomerDetails, 
        on_delete=models.CASCADE,
        related_name='bookings',
        null=False,
        help_text="Foreign key to CustomerDetails table"
    )
    
    # Add location_id as ForeignKey to Location table
    location_id = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='bookings_location',
        null=True,  # Set to True temporarily, adjust as needed
        help_text="Foreign key to Location table"
    )
    
    roller_id = models.CharField(max_length=50, blank=False, null=False)
    booking_unique_id = models.CharField(max_length=255, blank=True, null=True)
    booking_date = models.CharField(max_length=255, blank=True, null=True)
    booking_time = models.CharField(max_length=255, blank=True, null=True)
    payment_made = models.BooleanField(default=False)
    
    # Rename deposit_made to deposit_made_in_doller (note: corrected spelling to 'dollar')
    deposit_made_in_doller = models.FloatField(blank=True, null=True)
    
    # Add booking_status with default 'live'
    booking_status = models.CharField(
        max_length=50,
        default='live', 
    )
    
    # Add is_booking_paid with default False
    is_booking_paid = models.BooleanField(default=False)
    
    payload = models.JSONField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.booking_unique_id}"