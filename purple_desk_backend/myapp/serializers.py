from rest_framework import serializers
from .models import User


from myapp.model.locations_model import Location
from myapp.model.hours_of_operations_model import HoursOfOperation

from myapp.model.birthday_party_packages_model import BirthdayPartyPackage

from rest_framework import serializers
from myapp.model.jump_passes_model import JumpPass



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role', 'is_active')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_active')




class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'



# class HoursOfOperationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = HoursOfOperation
#         fields = "__all__"





class HoursOfOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoursOfOperation
        fields = [
            'hours_of_operation_id',
            'location',
            'hours_type',
            'schedule_with',
            'ages_allowed',
            'starting_date',
            'ending_date',
            'starting_day_name',
            'ending_day_name',
            'start_time',
            'end_time',
            'reason',
            'is_modified',
            'same_entry_id'  # ⬅️ ADD THIS LINE
        ]
        read_only_fields = ['hours_of_operation_id', 'same_entry_id']  # ⬅️ ADD same_entry_id here too

class BirthdayPartyPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirthdayPartyPackage
        fields = [
            'birthday_party_packages_id',
            'location',
            'package_name',
            'birthday_party_priority',
            'birthday_party_pitch',
            'availability_days',
            'schedule_with',
            'minimum_jumpers',
            'jump_time',
            'party_room_time',
            'food_and_drinks',
            'paper_goods',
            'skysocks',
            'dessert_policy',
            'other_perks',
            'outside_food_drinks_fee',
            'price',
            'guest_of_honour_included_in_total_jumpers',
            'tax_included',
            # 'tax_percentage',
            'each_additional_jump_hour_after_room_time',
            'can_custom_take_part_in_multiple'
            'additional_instructions',
            'birthday_party_booking_lead_allowed_days',
            'birthday_party_reschedule_allowed_days',
            'birthday_party_discount_code',
            'birthday_party_discount_percentage',
            'roller_birthday_party_search_id',
            'each_additional_jumper_price',
            'roller_additional_jumper_price_search_id',
            'roller_birthday_party_booking_id',
            'each_additional_jump_half_hour_after_room_time'
            'is_available',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['birthday_party_packages_id', 'created_at', 'updated_at']
        
    def validate_package_name(self, value):
        """Validate that package_name is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Package name cannot be empty")
        return value.strip()
        
    def validate_birthday_party_priority(self, value):
        """Validate that priority is a positive number"""
        if value <= 0:
            raise serializers.ValidationError("Birthday party priority must be a positive number")
        return value
        
    def validate_minimum_jumpers(self, value):
        """Validate that minimum_jumpers is a positive number"""
        if value <= 0:
            raise serializers.ValidationError("Minimum jumpers must be a positive number")
        return value
        
    def validate_price(self, value):
        """Validate that price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
        
    def validate_each_additional_jumper_price(self, value):
        """Validate that additional jumper price is positive"""
        if value < 0:
            raise serializers.ValidationError("Each additional jumper price cannot be negative")
        return value
        
    def validate_tax_included(self, value):
        """Validate tax percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Tax percentage must be between 0 and 100")
        return value
        
    def validate_birthday_party_booking_lead_allowed_days(self, value):
        """Validate booking lead days is positive"""
        if value <= 0:
            raise serializers.ValidationError("Booking lead allowed days must be a positive number")
        return value
        
    def validate_birthday_party_reschedule_allowed_days(self, value):
        """Validate reschedule days is positive"""
        if value <= 0:
            raise serializers.ValidationError("Reschedule allowed days must be a positive number")
        return value
    
    def validate(self, data):
        """Custom validation to check for duplicate package names within the same location"""
        package_name = data.get('package_name')
        location = data.get('location')
        
        if package_name and location:
            # Check if we're updating an existing record
            if self.instance:
                # For updates, exclude the current instance from the check
                existing_package = BirthdayPartyPackage.objects.filter(
                    package_name__iexact=package_name.strip(),
                    location=location
                ).exclude(birthday_party_packages_id=self.instance.birthday_party_packages_id).first()
            else:
                # For new records, check if any record with this name exists
                existing_package = BirthdayPartyPackage.objects.filter(
                    package_name__iexact=package_name.strip(),
                    location=location
                ).first()
            
            if existing_package:
                raise serializers.ValidationError({
                    'package_name': f"A birthday party package with the name '{package_name}' already exists for this location."
                })
        
        return data
    






class JumpPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = JumpPass
        fields = [
            'jump_pass_id',
            'location',
            'jump_pass_priority',
            'jump_pass_pitch',
            'schedule_with',
            'pass_name',
            'age_allowed',
            'starting_day_name',
            'ending_day_name',
            'jump_time_allowed',
            'price',
            'tax_included',
            # 'tax_percentage',
            'can_custom_take_part_in_multiple',
            'recommendation',
            'comments',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['jump_pass_id', 'created_at', 'updated_at']
        
    def validate_pass_name(self, value):
        """Validate that pass_name is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Pass name cannot be empty")
        return value.strip()
        
    def validate_jump_pass_priority(self, value):
        """Validate that priority is a positive number"""
        if value <= 0:
            raise serializers.ValidationError("Jump pass priority must be a positive number")
        return value
        
    def validate_price(self, value):
        """Validate that price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
        
    def validate_tax_included(self, value):
        """Validate tax percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Tax percentage must be between 0 and 100")
        return value
        
    # def validate_schedule_with(self, value):
    #     """Validate that schedule_with is not empty"""
    #     if not value or not value.strip():
    #         raise serializers.ValidationError("Schedule with cannot be empty")
    #     return value.strip()

    def validate_schedule_with(self, value):
        """Validate that schedule_with is a non-empty list of strings"""
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Schedule with must be a non-empty list.")
        # Optionally check that every element is a non-empty string
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise serializers.ValidationError("Each schedule type must be a non-empty string.")
        return value

        
    def validate_age_allowed(self, value):
        """Validate that age_allowed is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Age allowed cannot be empty")
        return value.strip()
        
    def validate_jump_time_allowed(self, value):
        """Validate that jump_time_allowed is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Jump time allowed cannot be empty")
        return value.strip()
        
    def validate_recommendation(self, value):
        """Validate that recommendation is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Recommendation cannot be empty")
        return value.strip()
    
    def validate(self, data):
        """Custom validation to check for duplicate pass names within the same location"""
        pass_name = data.get('pass_name')
        location = data.get('location')
        
        if pass_name and location:
            # Check if we're updating an existing record
            if self.instance:
                # For updates, exclude the current instance from the check
                existing_pass = JumpPass.objects.filter(
                    pass_name__iexact=pass_name.strip(),
                    location=location
                ).exclude(jump_pass_id=self.instance.jump_pass_id).first()
            else:
                # For new records, check if any record with this name exists
                existing_pass = JumpPass.objects.filter(
                    pass_name__iexact=pass_name.strip(),
                    location=location
                ).first()
            
            if existing_pass:
                raise serializers.ValidationError({
                    'pass_name': f"A jump pass with the name '{pass_name}' already exists for this location."
                })
        
        return data