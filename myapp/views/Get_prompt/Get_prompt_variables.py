from django.forms.models import model_to_dict
from myapp.model.locations_model import Location

async def Get_prompt_variables(location_id: int) -> dict:
    """
    Async function that returns all Location columns for a given location_id
    """
    try:
        location = await Location.objects.aget(location_id=location_id)
        return model_to_dict(location)
    except Location.DoesNotExist:
        return {}