import uuid
from django.db import models

class HoursOfOperation(models.Model):
    hours_of_operation_id = models.AutoField(primary_key=True)
    location = models.ForeignKey("Location", on_delete=models.CASCADE)  # FK Location_id
    hours_type = models.CharField(max_length=100)
    schedule_with = models.CharField(max_length=100,null=True, blank=True)
    ages_allowed = models.CharField(max_length=50,null=True, blank=True)
    starting_date = models.DateField(null=True, blank=True)
    ending_date = models.DateField(null=True, blank=True)
    starting_day_name = models.CharField(max_length=20)
    ending_day_name = models.CharField(max_length=20, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    is_modified = models.BooleanField(default=False)  # yes/no flag
    same_entry_id = models.UUIDField( null=True, blank=True, editable=False)

    class Meta:
        db_table = "hours_of_operation"
