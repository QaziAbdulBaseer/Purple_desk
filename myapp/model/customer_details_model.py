



from django.db import models
class CustomerDetails(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_email = models.CharField(max_length=255, blank=False, null=False)
    phone_number = models.CharField(max_length=15, blank=False, null=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255,blank=True, null=True)
    roller_customer_id = models.CharField(max_length=255, blank=True, null=True)

        
    def __str__(self):
        return f"{self.customer_id}"




