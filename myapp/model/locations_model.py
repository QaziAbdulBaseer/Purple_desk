from django.db import models

# Create your models here.


class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=255)
    location_address = models.TextField()
    location_timezone = models.CharField(max_length=100)
    location_call_number = models.CharField(max_length=20, blank=True, null=True)
    location_transfer_number = models.CharField(max_length=20, blank=True, null=True)
    location_google_map_link = models.URLField(max_length=500, blank=True, null=True)

    def _str_(self):
        return self.location_name