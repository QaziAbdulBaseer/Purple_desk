



from .models import User
from rest_framework import serializers
from myapp.model.faqs_model import FAQ
from myapp.model.policy_model import Policy
from myapp.model.locations_model import Location
from myapp.model.jump_passes_model import JumpPass
from myapp.model.promotions_model import Promotion
from myapp.model.membership_model import Membership
from myapp.model.group_booking_model import GroupBooking
from myapp.model.rental_facility_model import RentalFacility
from myapp.model.items_food_drinks_model import ItemsFoodDrinks
from myapp.model.hours_of_operations_model import HoursOfOperation
from myapp.model.balloon_party_packages_model import BalloonPartyPackage
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
            'same_entry_id'
        ]
        read_only_fields = ['hours_of_operation_id', 'same_entry_id']

# class BirthdayPartyPackageSerializer(serializers.ModelSerializer):
#     balloon_party_package_name = serializers.CharField(source='balloon_party_package.package_name', read_only=True)
    
#     class Meta:
#         model = BirthdayPartyPackage
#         fields = [
#             'birthday_party_packages_id',
#             'location',
#             'package_name',
#             'birthday_party_priority',
#             'birthday_party_pitch',
#             'availability_days',
#             'schedule_with',
#             'minimum_jumpers',
#             'jump_time',
#             'party_room_time',
#             'food_and_drinks',
#             'paper_goods',
#             'skysocks',
#             'dessert_policy',
#             'other_perks',
#             'outside_food_drinks_fee',
#             'price',
#             'guest_of_honour_included_in_total_jumpers',
#             'tax_included',
#             'each_additional_jump_hour_after_room_time',
#             'additional_instructions',
#             'birthday_party_booking_lead_allowed_days',
#             'birthday_party_reschedule_allowed_days',
#             'birthday_party_discount_code',
#             'birthday_party_discount_percentage',
#             'roller_birthday_party_search_id',
#             'each_additional_jumper_price',
#             'roller_additional_jumper_price_search_id',
#             'roller_birthday_party_booking_id',
#             'each_additional_jump_half_hour_after_room_time',
#             'is_available',
#             'Is_additional_jumpers_allowed',
#             'created_at',
#             'updated_at',
#             # New fields
#             'balloon_package_included',
#             'promotion_code',
#             'credit',
#             'balloon_party_package',
#             'balloon_party_package_name'
#         ]
#         read_only_fields = ['birthday_party_packages_id', 'created_at', 'updated_at']
        
#     def validate_package_name(self, value):
#         """Validate that package_name is not empty"""
#         if not value or not value.strip():
#             raise serializers.ValidationError("Package name cannot be empty")
#         return value.strip()
        
#     def validate_birthday_party_priority(self, value):
#         """Validate that priority is a positive number"""
#         if value <= 0:
#             raise serializers.ValidationError("Birthday party priority must be a positive number")
#         return value
        
#     def validate_minimum_jumpers(self, value):
#         """Validate that minimum_jumpers is a positive number"""
#         if value <= 0:
#             raise serializers.ValidationError("Minimum jumpers must be a positive number")
#         return value
        
#     def validate_price(self, value):
#         """Validate that price is positive"""
#         if value <= 0:
#             raise serializers.ValidationError("Price must be greater than 0")
#         return value
        
#     def validate_each_additional_jumper_price(self, value):
#         """Validate that additional jumper price is positive"""
#         if value < 0:
#             raise serializers.ValidationError("Each additional jumper price cannot be negative")
#         return value
        
#     def validate_birthday_party_booking_lead_allowed_days(self, value):
#         """Validate booking lead days is positive"""
#         if value <= 0:
#             raise serializers.ValidationError("Booking lead allowed days must be a positive number")
#         return value
        
#     def validate_birthday_party_reschedule_allowed_days(self, value):
#         """Validate reschedule days is positive"""
#         if value <= 0:
#             raise serializers.ValidationError("Reschedule allowed days must be a positive number")
#         return value
    
#     def validate(self, data):
#         """Custom validation to check for duplicate package names within the same location"""
#         package_name = data.get('package_name')
#         location = data.get('location')
        
#         if package_name and location:
#             # Check if we're updating an existing record
#             if self.instance:
#                 # For updates, exclude the current instance from the check
#                 existing_package = BirthdayPartyPackage.objects.filter(
#                     package_name__iexact=package_name.strip(),
#                     location=location
#                 ).exclude(birthday_party_packages_id=self.instance.birthday_party_packages_id).first()
#             else:
#                 # For new records, check if any record with this name exists
#                 existing_package = BirthdayPartyPackage.objects.filter(
#                     package_name__iexact=package_name.strip(),
#                     location=location
#                 ).first()
            
#             if existing_package:
#                 raise serializers.ValidationError({
#                     'package_name': f"A birthday party package with the name '{package_name}' already exists for this location."
#                 })
        
#         return data




# class BirthdayPartyPackageSerializer(serializers.ModelSerializer):
#     balloon_party_package_name = serializers.CharField(source='balloon_party_package.package_name', read_only=True)
    
#     class Meta:
#         model = BirthdayPartyPackage
#         fields = [
#             'birthday_party_packages_id',
#             'location',
#             'package_name',
#             'birthday_party_priority',
#             'birthday_party_pitch',
#             'availability_days',
#             'schedule_with',
#             'minimum_jumpers',
#             'jump_time',
#             'party_room_time',
#             'food_and_drinks',
#             'paper_goods',
#             'skysocks',
#             'dessert_policy',
#             'other_perks',
#             'outside_food_drinks_fee',
#             'price',
#             'guest_of_honour_included_in_total_jumpers',
#             'tax_included',
#             'each_additional_jump_hour_after_room_time',
#             'additional_instructions',
#             'birthday_party_booking_lead_allowed_days',
#             'birthday_party_reschedule_allowed_days',
#             'birthday_party_discount_code',
#             'birthday_party_discount_percentage',
#             'roller_birthday_party_search_id',
#             'each_additional_jumper_price',
#             'roller_additional_jumper_price_search_id',
#             'roller_birthday_party_booking_id',
#             'each_additional_jump_half_hour_after_room_time',
#             'is_available',
#             'Is_additional_jumpers_allowed',
#             'created_at',
#             'updated_at',
#             # New fields
#             'balloon_package_included',
#             'promotion_code',
#             'credit',
#             'balloon_party_package',
#             'balloon_party_package_name',
#             # NEW FIELD: is_any_balloon_package_is_free
#             'is_any_balloon_package_is_free'
#         ]
#         read_only_fields = ['birthday_party_packages_id', 'created_at', 'updated_at']
        
#     def validate_package_name(self, value):
#         """Validate that package_name is not empty"""
#         if not value or not value.strip():
#             raise serializers.ValidationError("Package name cannot be empty")
#         return value.strip()
        
#     def validate_birthday_party_priority(self, value):
#         """Validate that priority is a positive number"""
#         if value <= 0:
#             raise serializers.ValidationError("Birthday party priority must be a positive number")
#         return value
        
#     def validate_minimum_jumpers(self, value):
#         """Validate that minimum_jumpers is a positive number"""
#         if value <= 0:
#             raise serializers.ValidationError("Minimum jumpers must be a positive number")
#         return value
        
#     def validate_price(self, value):
#         """Validate that price is positive"""
#         if value <= 0:
#             raise serializers.ValidationError("Price must be greater than 0")
#         return value
        
#     def validate_each_additional_jumper_price(self, value):
#         """Validate that additional jumper price is positive"""
#         if value < 0:
#             raise serializers.ValidationError("Each additional jumper price cannot be negative")
#         return value
        
#     def validate_birthday_party_booking_lead_allowed_days(self, value):
#         """Validate booking lead days is positive"""
#         if value <= 0:
#             raise serializers.ValidationError("Booking lead allowed days must be a positive number")
#         return value
        
#     def validate_birthday_party_reschedule_allowed_days(self, value):
#         """Validate reschedule days is positive"""
#         if value <= 0:
#             raise serializers.ValidationError("Reschedule allowed days must be a positive number")
#         return value
    
#     def validate(self, data):
#         """Custom validation to check for duplicate package names within the same location"""
#         package_name = data.get('package_name')
#         location = data.get('location')
        
#         if package_name and location:
#             # Check if we're updating an existing record
#             if self.instance:
#                 # For updates, exclude the current instance from the check
#                 existing_package = BirthdayPartyPackage.objects.filter(
#                     package_name__iexact=package_name.strip(),
#                     location=location
#                 ).exclude(birthday_party_packages_id=self.instance.birthday_party_packages_id).first()
#             else:
#                 # For new records, check if any record with this name exists
#                 existing_package = BirthdayPartyPackage.objects.filter(
#                     package_name__iexact=package_name.strip(),
#                     location=location
#                 ).first()
            
#             if existing_package:
#                 raise serializers.ValidationError({
#                     'package_name': f"A birthday party package with the name '{package_name}' already exists for this location."
#                 })
        
#         return data


class BirthdayPartyPackageSerializer(serializers.ModelSerializer):
    balloon_party_package_name = serializers.CharField(source='balloon_party_package.package_name', read_only=True)
    
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
            # REMOVED: 'birthday_party_booking_lead_allowed_days',
            # REMOVED: 'birthday_party_reschedule_allowed_days',
            'birthday_party_discount_code',
            'birthday_party_discount_percentage',
            'roller_birthday_party_search_id',
            'each_additional_jumper_price',
            'roller_additional_jumper_price_search_id',
            'roller_birthday_party_booking_id',
            'each_additional_jump_half_hour_after_room_time',
            'is_available',
            'Is_additional_jumpers_allowed',
            'created_at',
            'updated_at',
            # Balloon package fields
            'balloon_package_included',
            'promotion_code',
            'credit',
            'balloon_party_package',
            'balloon_party_package_name',
            'is_any_balloon_package_is_free',
            # NEW FIELDS
            'party_environment_name',
            'food_included_count',
            'drinks_included_count',
            'perks_for_guest_of_honor'
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
        
    # REMOVED: validate_birthday_party_booking_lead_allowed_days
    # REMOVED: validate_birthday_party_reschedule_allowed_days
    
    def validate_food_included_count(self, value):
        """Validate that food_included_count is not negative"""
        if value and value < 0:
            raise serializers.ValidationError("Food included count cannot be negative")
        return value
        
    def validate_drinks_included_count(self, value):
        """Validate that drinks_included_count is not negative"""
        if value and value < 0:
            raise serializers.ValidationError("Drinks included count cannot be negative")
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


# class JumpPassSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = JumpPass
#         fields = [
#             'jump_pass_id',
#             'location',
#             'jump_pass_priority',
#             'jump_pass_pitch',
#             'schedule_with',
#             'pass_name',
#             'age_allowed',
#             'starting_day_name',
#             'ending_day_name',
#             'jump_time_allowed',
#             'price',
#             'tax_included',
#             'can_custom_take_part_in_multiple',
#             'recommendation',
#             'comments',
#             'roller_booking_id',
#             'created_at',
#             'updated_at'
#         ]
#         read_only_fields = ['jump_pass_id', 'created_at', 'updated_at']


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
            'can_custom_take_part_in_multiple',
            'recommendation',
            'comments',
            'roller_booking_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['jump_pass_id', 'created_at', 'updated_at']

    def validate_roller_booking_id(self, value):
        """Custom validation to allow multiple NULLs but enforce uniqueness for non-NULL values"""
        if value is not None and value.strip():  # If value is not None and not empty string
            # Check if another JumpPass with the same non-NULL roller_booking_id exists
            if JumpPass.objects.filter(roller_booking_id=value).exists():
                # If we're updating an existing instance, exclude it from the check
                if self.instance and self.instance.roller_booking_id == value:
                    return value
                raise serializers.ValidationError("A jump pass with this roller booking ID already exists.")
        return value


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = [
            'membership_id',
            'location',
            'title',
            'schedule_with',
            'pitch_priority',
            'pitch_introduction',
            'activity_time',
            'features',
            'valid_until',
            'party_discount',
            'price',
            'parent_addon_price',
            'subscription',
            'tax_included',
            'created_at',
            'updated_at'
        ]

class BalloonPartyPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalloonPartyPackage
        fields = [
            'balloon_party_packages_id',
            'package_name',
            'call_flow_priority',
            'promotional_pitch',
            'package_inclusions',
            'discount',
            'price',
            'note',
            'location',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['balloon_party_packages_id', 'created_at', 'updated_at']

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = [
            'faq_id',
            'location',
            'question_type',
            'question',
            'answer',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['faq_id', 'created_at', 'updated_at']

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = [
            'policy_id',
            'location',
            'policy_type',
            'details',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['policy_id', 'created_at', 'updated_at']

class PolicyBulkCreateSerializer(serializers.Serializer):
    policies = PolicySerializer(many=True)

class PromotionSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Promotion
        fields = [
            'promotion_id',
            'location',
            'start_date',
            'end_date',
            'start_day',
            'end_day',
            'start_time',
            'end_time',
            'schedule_type',
            'promotion_code',
            'title',
            'details',
            'category',
            'sub_category',
            'eligibility_type',
            'constraint_value',
            'instructions',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['promotion_id', 'created_at', 'updated_at', 'is_active']

class ItemsFoodDrinksSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.location_name', read_only=True)
    t_shirt_sizes_list = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ItemsFoodDrinks
        fields = [
            'item_id',
            'location',
            'location_name',
            'category',
            'category_priority',
            'category_type',
            'options_type_per_category',
            'additional_instructions',
            'item',
            'price',
            't_shirt_sizes',
            't_shirt_sizes_list',
            't_shirt_type',
            'pitch_in_party_package',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['item_id', 'created_at', 'updated_at']
    
    def get_t_shirt_sizes_list(self, obj):
        return obj.get_t_shirt_sizes_list()








class RentalFacilitySerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.location_name', read_only=True)
    
    class Meta:
        model = RentalFacility
        fields = [
            'rental_facility_id',
            'location',
            'location_name',
            'rental_jumper_group',
            'call_flow_priority',
            'per_jumper_price',
            'minimum_jumpers',
            'instruction',
            'inclusions',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['rental_facility_id', 'created_at', 'updated_at']
        
    def validate_rental_jumper_group(self, value):
        """Validate that rental_jumper_group is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Rental jumper group cannot be empty")
        return value.strip()
        
    def validate_call_flow_priority(self, value):
        """Validate that call_flow_priority is a positive number"""
        if value <= 0:
            raise serializers.ValidationError("Call flow priority must be a positive number")
        return value
        
    def validate_per_jumper_price(self, value):
        """Validate that per_jumper_price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Per jumper price must be greater than 0")
        return value
        
    def validate_minimum_jumpers(self, value):
        """Validate that minimum_jumpers is a positive number"""
        if value <= 0:
            raise serializers.ValidationError("Minimum jumpers must be a positive number")
        return value
    
    def validate(self, data):
        """Custom validation to check for duplicate rental_jumper_group within the same location"""
        rental_jumper_group = data.get('rental_jumper_group')
        location = data.get('location')
        
        if rental_jumper_group and location:
            # Check if we're updating an existing record
            if self.instance:
                # For updates, exclude the current instance from the check
                existing_facility = RentalFacility.objects.filter(
                    rental_jumper_group__iexact=rental_jumper_group.strip(),
                    location=location
                ).exclude(rental_facility_id=self.instance.rental_facility_id).first()
            else:
                # For new records, check if any record with this name exists
                existing_facility = RentalFacility.objects.filter(
                    rental_jumper_group__iexact=rental_jumper_group.strip(),
                    location=location
                ).first()
            
            if existing_facility:
                raise serializers.ValidationError({
                    'rental_jumper_group': f"A rental facility with the name '{rental_jumper_group}' already exists for this location."
                })
        
        return data





class GroupBookingSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.location_name', read_only=True)
    
    class Meta:
        model = GroupBooking
        fields = [
            'group_booking_id',
            'location',
            'location_name',
            'group_packages',
            'call_flow_priority',
            'flat_fee_jumper_price',
            'minimum_jumpers',
            'instruction',
            'package_inclusions',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['group_booking_id', 'created_at', 'updated_at']
        
    def validate_group_packages(self, value):
        """Validate that group_packages is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Group packages cannot be empty")
        return value.strip()
        
    def validate_call_flow_priority(self, value):
        """Validate that call_flow_priority is a positive number"""
        if value <= 0:
            raise serializers.ValidationError("Call flow priority must be a positive number")
        return value
        
    def validate_flat_fee_jumper_price(self, value):
        """Validate that flat_fee_jumper_price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Flat fee jumper price must be greater than 0")
        return value
        
    def validate_minimum_jumpers(self, value):
        """Validate that minimum_jumpers is a positive number"""
        if value <= 0:
            raise serializers.ValidationError("Minimum jumpers must be a positive number")
        return value
    
    def validate(self, data):
        """Custom validation to check for duplicate group_packages within the same location"""
        group_packages = data.get('group_packages')
        location = data.get('location')
        
        if group_packages and location:
            # Check if we're updating an existing record
            if self.instance:
                # For updates, exclude the current instance from the check
                existing_booking = GroupBooking.objects.filter(
                    group_packages__iexact=group_packages.strip(),
                    location=location
                ).exclude(group_booking_id=self.instance.group_booking_id).first()
            else:
                # For new records, check if any record with this name exists
                existing_booking = GroupBooking.objects.filter(
                    group_packages__iexact=group_packages.strip(),
                    location=location
                ).first()
            
            if existing_booking:
                raise serializers.ValidationError({
                    'group_packages': f"A group booking with the name '{group_packages}' already exists for this location."
                })
        
        return data