from rest_framework import serializers
from .models import User


from myapp.model.locations_model import Location
from myapp.model.hours_of_operations_model import HoursOfOperation

from myapp.model.birthday_party_packages_model import BirthdayPartyPackage



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



class HoursOfOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoursOfOperation
        fields = "__all__"






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
            'each_additional_jump_hour_after_room_time',
            'additional_instructions',
            'birthday_party_booking_lead_allowed_days',
            'birthday_party_reschedule_allowed_days',
            'birthday_party_discount_code',
            'birthday_party_discount_percentage',
            'roller_birthday_party_search_id',
            'each_additional_jumper_price',
            'roller_additional_jumper_price_search_id',
            'roller_birthday_party_booking_id',
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