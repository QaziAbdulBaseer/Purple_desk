from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
from myapp.model.locations_model import Location


async def get_current_date_by_location(location_id: int) -> str:
    """
    Returns current date based on the location's timezone
    """
    location = await Location.objects.aget(location_id=location_id)
    tz = ZoneInfo(location.location_timezone)
    return datetime.now(tz).date().isoformat()


async def get_current_time_by_location(location_id: int) -> str:
    """
    Returns current time based on the location's timezone
    """
    location = await Location.objects.aget(location_id=location_id)
    tz = ZoneInfo(location.location_timezone)
    return datetime.now(tz).strftime("%H:%M:%S")
