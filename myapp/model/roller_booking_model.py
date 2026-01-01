



from django.db import models

from myapp.model.customer_details_model import CustomerDetails
class RollerBookingDetails(models.Model):
    booking_id = models.AutoField(primary_key=True)
    # customer_id = models.CharField(max_length=255, blank=False, null=False) # ITS FOREIGN KEY
    customer = models.ForeignKey(
        CustomerDetails, 
        on_delete=models.CASCADE,
        related_name='bookings',
        null=False,  # Making it non-nullable since you said it's required
        help_text="Foreign key to CustomerDetails table"
    )
    roller_id = models.CharField(max_length=50, blank=False, null=False)
    booking_unique_id = models.CharField(max_length=255, blank=True, null=True)
    booking_date = models.CharField(max_length=255,blank=True, null=True)
    booking_time = models.CharField(max_length=255, blank=True, null=True)
    capacity_reservation_id = models.CharField(max_length=255, blank=True, null=True)
    payment_made = models.BooleanField(default=False)
    payload = models.JSONField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now=True)

        
    def __str__(self):
        return f"{self.roller_booking_id}"



