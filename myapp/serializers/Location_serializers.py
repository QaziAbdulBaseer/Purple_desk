from rest_framework import serializers
from myapp.model.locations_model import Location

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "_all_"

    def validate(self, data):
        for field in ["location_name", "location_address", "location_timezone",
                      "location_call_number", "location_transfer_number",
                      "location_google_map_link"]:
            if not data.get(field):
                raise serializers.ValidationError({field: f"{field} is required"})
        return data