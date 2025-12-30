# # from rest_framework import serializers
# # from myapp.model.locations_model import Location

# # class LocationSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Location
# #         fields = "_all_"

# #     def validate(self, data):
# #         for field in ["location_name", "location_address", "location_timezone",
# #                       "location_call_number", "location_transfer_number",
# #                       "location_google_map_link"]:
# #             if not data.get(field):
# #                 raise serializers.ValidationError({field: f"{field} is required"})
# #         return data



# from rest_framework import serializers
# from myapp.model.locations_model import Location

# class LocationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Location
#         fields = "__all__"
#         # Make the token fields read-only so they can't be set via API
#         read_only_fields = ('roller_access_token', 'roller_token_created_at', 'location_id')

#     def validate(self, data):
#         # Existing validation
#         for field in ["location_name", "location_address", "location_timezone",
#                       "location_call_number", "location_transfer_number",
#                       "location_google_map_link"]:
#             if not data.get(field):
#                 raise serializers.ValidationError({field: f"{field} is required"})
        
#         # --- ADD THIS VALIDATION FOR NEW FIELDS ---
#         roller_client_id = data.get('roller_client_id')
#         roller_client_secret = data.get('roller_client_secret')
        
#         # If either client_id or client_secret is provided, both must be provided
#         if bool(roller_client_id) != bool(roller_client_secret):
#             raise serializers.ValidationError(
#                 "Both roller_client_id and roller_client_secret must be provided together or both left blank"
#             )
#         # --- END OF NEW VALIDATION ---
        
#         return data



from rest_framework import serializers
from myapp.model.locations_model import Location
import requests
from django.utils import timezone

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"
        read_only_fields = ('roller_access_token', 'roller_token_created_at', 'location_id')

    def validate(self, data):
        # Existing validation for required fields
        for field in ["location_name", "location_address", "location_timezone",
                      "location_call_number", "location_transfer_number",
                      "location_google_map_link"]:
            if not data.get(field):
                raise serializers.ValidationError({field: f"{field} is required"})
        
        # New validation for Roller API fields
        roller_client_id = data.get('roller_client_id')
        roller_client_secret = data.get('roller_client_secret')
        
        # If either client_id or client_secret is provided, both must be provided
        if bool(roller_client_id) != bool(roller_client_secret):
            raise serializers.ValidationError(
                "Both roller_client_id and roller_client_secret must be provided together or both left blank"
            )
        
        return data

    def create(self, validated_data):
        """Override create to generate token if credentials are provided"""
        roller_client_id = validated_data.get('roller_client_id')
        roller_client_secret = validated_data.get('roller_client_secret')
        
        # Create the location first
        location = super().create(validated_data)
        
        # If credentials are provided, generate token
        if roller_client_id and roller_client_secret:
            try:
                token = self.generate_roller_token(roller_client_id, roller_client_secret)
                if token:
                    location.roller_access_token = token
                    location.roller_token_created_at = timezone.now()
                    location.save(update_fields=['roller_access_token', 'roller_token_created_at'])
            except Exception as e:
                # Don't fail the creation if token generation fails
                # The token can be generated later
                print(f"Token generation failed during creation: {str(e)}")
        
        return location

    def update(self, instance, validated_data):
        """Override update to update token if credentials are changed"""
        old_client_id = instance.roller_client_id
        old_client_secret = instance.roller_client_secret
        
        new_client_id = validated_data.get('roller_client_id')
        new_client_secret = validated_data.get('roller_client_secret')
        
        # Update the location first
        location = super().update(instance, validated_data)
        
        # Check if credentials were changed
        if (new_client_id and new_client_secret and 
            (old_client_id != new_client_id or old_client_secret != new_client_secret)):
            try:
                token = self.generate_roller_token(new_client_id, new_client_secret)
                if token:
                    location.roller_access_token = token
                    location.roller_token_created_at = timezone.now()
                    location.save(update_fields=['roller_access_token', 'roller_token_created_at'])
            except Exception as e:
                print(f"Token generation failed during update: {str(e)}")
        
        return location

    def generate_roller_token(self, client_id, client_secret):
        """Generate Roller API token"""
        url = "https://api.haveablast.roller.app/token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("access_token")
        except Exception as e:
            print(f"Error generating token: {str(e)}")
            return None