
# hi, i have to make a new table. then I have to write a crud operation for that table. and creat the apis end points. 
# i give you tables colums name, and also give you an example code. how i am doing work
# so you have to tell me which new file i have to create and which code i have to past. 
# the new table is == 
# Table: FAQs

# Location_id (FK)

# FAQs_id (PK)

# question_type

# question

# answer
# this is my file structure = 
# (venv) PS D:\Sybrid\purple_desk\New_purple_desk\New_purple_desk_backend\myapp> tree /f
# Folder PATH listing for volume Data center
# Volume serial number is C6C6-DE32
# D:.
# │   admin.py
# │   apps.py
# │   models.py
# │   serializers.py
# │   urls.py
# │   viewsww.py
# │   __init__.py
# │
# ├───migrations
# │   │   0001_initial.py
# │   │   0002_alter_birthdaypartypackage_tax_included.py
# │   │   __init__.py
# │   │
# │   └───__pycache__
# │           0001_initial.cpython-39.pyc
# │           0002_alter_birthdayballoonbridge_balloon_party_package_and_more.cpython-39.pyc
# │           0002_alter_birthdaypartypackage_tax_included.cpython-39.pyc
# │           0003_alter_birthdayballoonbridge_balloon_party_package_and_more.cpython-39.pyc
# │           __init__.cpython-39.pyc
# │
# ├───model
# │   │   balloon_party_packages_model.py
# │   │   birthday_balloon_bridge_model.py
# │   │   birthday_party_packages_model.py
# │   │   hours_of_operations_model.py
# │   │   jump_passes_model.py
# │   │   locations_model.py
# │   │   membership_model.py
# │   │
# │   └───__pycache__
# │           balloon_party_packages_model.cpython-39.pyc
# │           birthday_balloon_bridge_model.cpython-39.pyc
# │           birthday_party_packages_model.cpython-39.pyc
# │           hours_of_operations_model.cpython-39.pyc
# │           jump_passes_model.cpython-311.pyc
# │           jump_passes_model.cpython-39.pyc
# │           locations_model.cpython-39.pyc
# │           membership_model.cpython-39.pyc
# │
# ├───serializers
# │       Location_serializers.py
# │
# ├───views
# │   │   View_Authorization.py
# │   │   View_balloon_party_packages.py
# │   │   View_birthday_balloon_bridge.py
# │   │   View_birthday_party_packages.py
# │   │   View_Get_Prompt.py
# │   │   View_hours_of_operations.py
# │   │   View_jump_passes.py
# │   │   View_Locations.py
# │   │   View_membership.py
# │   │
# │   ├───Get_prompt
# │   │   │   Get_hours_of_operation.py
# │   │   │   Get_jump_pass.py
# │   │   │   Get_membership.py
# │   │   │   Get_membershipEXP.py
# │   │   │
# │   │   └───__pycache__
# │   │           Get_hours_of_operation.cpython-39.pyc
# │   │           Get_jump_pass.cpython-39.pyc
# │   │           Get_membership.cpython-39.pyc
# │   │
# │   └───__pycache__
# │           View_Authorization.cpython-39.pyc
# │           View_balloon_party_packages.cpython-39.pyc
# │           View_birthday_balloon_bridge.cpython-39.pyc
# │           View_birthday_party_packages.cpython-39.pyc
# │           View_Get_Prompt.cpython-39.pyc
# │           View_hours_of_operations.cpython-39.pyc
# │           View_jump_passes.cpython-311.pyc
# │           View_jump_passes.cpython-39.pyc
# │           View_Locations.cpython-39.pyc
# │           View_membership.cpython-39.pyc
# │
# └───__pycache__
#         admin.cpython-39.pyc
#         apps.cpython-39.pyc
#         models.cpython-39.pyc
#         serializers.cpython-39.pyc
#         urls.cpython-39.pyc
#         __init__.cpython-39.pyc

# (venv) PS D:\Sybrid\purple_desk\New_purple_desk\New_purple_desk_backend\myapp> 



# this is one example model of the membership =-= = = 

from django.db import models
from myapp.model.locations_model import Location
from django.db.models import JSONField

class Membership(models.Model):
    membership_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='memberships')
    
    # Required fields
    title = models.CharField(max_length=255, blank=False, null=False , unique=True)
    schedule_with = models.JSONField(default=list, null=False, blank=False)
    pitch_priority = models.IntegerField(null=False, blank=False)
    
    # Optional fields
    pitch_introduction = models.TextField(blank=True, null=True)
    activity_time = models.TextField(blank=True, null=True)
    features = models.TextField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)
    party_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    parent_addon_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    subscription = models.CharField(max_length=255, blank=True, null=True)
    tax_included = models.BooleanField(
        null=False,
        blank=False,
        help_text="Check if tax is included in the price (Yes/No or 1/0)."
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'memberships'
        ordering = ['pitch_priority']
        
    def __str__(self):
        return f"{self.title} - {self.location.location_name}"





# This is the example of the view_membership code. 

