

import asyncio
import pandas as pd
from datetime import datetime, timedelta, date
from typing import List, Tuple, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import pytz

# Import your Django models
from myapp.model.hours_of_operations_model import HoursOfOperation
from asgiref.sync import sync_to_async



async def get_hours_data_from_db(location_id: int) -> pd.DataFrame:
    """Fetch hours of operation data from database and convert to DataFrame"""
    
    def _fetch_hours_data():
        # Get all hours of operation for the location
        hours_queryset = HoursOfOperation.objects.filter(location_id=location_id)
        
        # Convert to list of dictionaries with proper null handling
        hours_data = []
        for hour in hours_queryset:
            # Convert times to AM/PM format for display
            start_time_str = ""
            end_time_str = ""
            
            if hour.start_time:
                # Convert to AM/PM format
                start_time_str = hour.start_time.strftime("%I:%M %p").lstrip('0')
                if start_time_str.startswith(':'):
                    start_time_str = '12' + start_time_str
            
            if hour.end_time:
                # Convert to AM/PM format  
                end_time_str = hour.end_time.strftime("%I:%M %p").lstrip('0')
                if end_time_str.startswith(':'):
                    end_time_str = '12' + end_time_str
            
            hour_data = {
                'hours_type': hour.hours_type or "",
                'schedule_with': hour.schedule_with or "",
                'ages_allowed': hour.ages_allowed or "",
                'starting_date': hour.starting_date.isoformat() if hour.starting_date else "",
                'ending_date': hour.ending_date.isoformat() if hour.ending_date else "",
                'starting_day_name': hour.starting_day_name or "",
                'ending_day_name': hour.ending_day_name or "",
                'start_time': start_time_str,
                'end_time': end_time_str,
                'reason': hour.reason or ""
            }
            hours_data.append(hour_data)
        
        # Create DataFrame
        df = pd.DataFrame(hours_data)
        
        # Print for debugging
        # print("Raw data from database (with AM/PM times):")
        # for i, row in df.iterrows():
        #     print(f"{i:2} {row['hours_type']:12} {str(row['schedule_with']):15} {str(row['ages_allowed']):15} {str(row['starting_date']):15} {str(row['ending_date']):15} {str(row['starting_day_name']):15} {str(row['ending_day_name']):15} {str(row['start_time']):10} {str(row['end_time']):10} {str(row['reason']):10}")
        
        # Rename 'schedule_with' to 'jump_type' to match your existing code
        if 'schedule_with' in df.columns:
            df = df.rename(columns={'schedule_with': 'jump_type'})
        
        return df
    
    # Run the database query in a thread
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _fetch_hours_data)




async def get_california_time(timezone):
    """Get current California time"""
    california_tz = pytz.timezone(timezone)
    return datetime.now(california_tz)

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object (timezone-naive)"""
    if not date_str or date_str == "nan" or date_str == "" or pd.isna(date_str) or date_str == "NaT":
        return None
    
    # Handle datetime objects directly
    if isinstance(date_str, datetime):
        return date_str.replace(tzinfo=None)
    
    # Handle date objects
    if isinstance(date_str, date):
        return datetime.combine(date_str, datetime.min.time())
    
    date_str = str(date_str).strip()
    
    try:
        # Try database date format first (YYYY-MM-DD)
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        try:
            # Try formatted date (January 01,2024)
            return datetime.strptime(date_str, "%B %d,%Y")
        except:
            try:
                # Try formatted date with space (January 01, 2024)
                return datetime.strptime(date_str, "%B %d, %Y")
            except:
                return None

async def get_next_seven_days_async(start_date: datetime) -> List[Tuple[str, str, datetime]]:
    """Get the next 7 days starting from the current date (including current date) - async version"""
    def _compute_days():
        days = []
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            day_name = current_date.strftime("%A")
            formatted_date = current_date.strftime("%B %d,%Y")
            days.append((day_name, formatted_date, current_date))
        return days
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _compute_days)
    

def clean_time(t):
    """Convert time to AM/PM format with proper cleaning"""
    if pd.isna(t) or t is None or t == "" or t == "NaT":
        return ""
    
    # Handle time objects directly - convert to string first
    if hasattr(t, 'strftime'):
        # If it's a time object, convert to string in 24-hour format first
        t = t.strftime("%H:%M:%S")
    
    t = str(t).strip()
    if not t:
        return t

    # Remove any extra spaces and ensure proper formatting
    t = t.replace('  ', ' ').strip()
    
    # If it's already in AM/PM format, just clean it up
    if 'AM' in t.upper() or 'PM' in t.upper():
        parts = t.split(':')
        hour = parts[0].lstrip('0') or '12'  # Handle 00 as 12
        
        if len(parts) > 1:
            minute_part = parts[1]
            # Extract minute and AM/PM
            if ' ' in minute_part:
                minute, am_pm = minute_part.split(' ', 1)
            else:
                minute = minute_part
                am_pm = ''
            
            # Clean up minute
            minute = minute.strip()
            if minute == '00':
                return f"{hour} {am_pm}".strip()
            else:
                return f"{hour}:{minute} {am_pm}".strip()
        else:
            return f"{hour} {t.split()[-1]}" if len(t.split()) > 1 else hour
    
    # Handle 24-hour format (HH:MM:SS or HH:MM)
    try:
        # Try to parse as time object
        if ':' in t:
            time_parts = t.split(':')
            hours = int(time_parts[0])
            minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
            
            # Convert to AM/PM format
            if hours == 0:
                return f"12:{minutes:02d} AM" if minutes > 0 else "12 AM"
            elif hours == 12:
                return f"12:{minutes:02d} PM" if minutes > 0 else "12 PM"
            elif hours < 12:
                return f"{hours}:{minutes:02d} AM" if minutes > 0 else f"{hours} AM"
            else:
                return f"{hours-12}:{minutes:02d} PM" if minutes > 0 else f"{hours-12} PM"
        else:
            # Just hours
            hours = int(t)
            if hours == 0:
                return "12 AM"
            elif hours == 12:
                return "12 PM"
            elif hours < 12:
                return f"{hours} AM"
            else:
                return f"{hours-12} PM"
    except (ValueError, IndexError):
        # If parsing fails, return the original string
        return t


def format_time_range(start_time: str, end_time: str) -> str:
    """Format time range in AM/PM format"""
    start_clean = clean_time(start_time)
    end_clean = clean_time(end_time)
    
    if start_clean and end_clean:
        return f"{start_clean} to {end_clean}"
    return ""



def format_time_range(start_time: str, end_time: str) -> str:
    start_clean = clean_time(start_time)
    end_clean = clean_time(end_time)
    
    if start_clean and end_clean:
        return f"{start_clean} to {end_clean}"
    return ""


def time_to_minutes(time_str: str) -> int:
    """Convert time string (e.g., '11 AM', '12 PM') to minutes since midnight"""
    if not time_str or pd.isna(time_str) or time_str == "":
        return 0
    
    time_str = str(time_str).strip().upper()
    
    # Handle time objects directly
    if hasattr(time_str, 'strftime'):
        time_str = time_str.strftime("%I:%M %p")
    
    # Handle AM/PM format
    if 'AM' in time_str or 'PM' in time_str:
        # Remove AM/PM and split
        time_part = time_str.replace('AM', '').replace('PM', '').strip()
        parts = time_part.split(':')
        
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0
        
        # Convert to 24-hour format
        if 'PM' in time_str and hour != 12:
            hour += 12
        elif 'AM' in time_str and hour == 12:
            hour = 0
            
        return hour * 60 + minute
    
    # Handle 24-hour format (HH:MM:SS)
    parts = time_str.split(':')
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    
    return hour * 60 + minute


def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight back to time string"""
    hours = minutes // 60
    mins = minutes % 60
    time_obj = datetime.strptime(f"{hours:02d}:{mins:02d}", "%H:%M")
    return time_obj.strftime("%I:%M %p")



def get_event_schedule_for_date_with_overlaps(jump_df: pd.DataFrame, target_date: datetime, day_name: str, 
                                            early_close_time: str = None, late_open_time: str = None,
                                            all_special_hours: Dict = None) -> List[Dict]:
    """Get schedule for a specific jump type on a specific date with overlap detection"""
    schedule = []
    target_date_str = target_date.strftime("%B %d,%Y")
    
    # DEBUG: Print special hours for troubleshooting
    special_hours = jump_df[jump_df["hours_type"] == "special"]
    # print(f"Found {len(special_hours)} special hours for {target_date.date()}")
    
    # Check for special hours first
    special_found = False
    
    for _, row in special_hours.iterrows():
        start_date = parse_date(row["starting_date"])
        end_date = parse_date(row["ending_date"])
        
        # print(f"Special hour: start={start_date}, end={end_date}, target={target_date.date()}, jump_type={row['jump_type']}")
        
        # Check if target date falls within special hours range
        if start_date and end_date:
            if start_date.date() <= target_date.date() <= end_date.date():
                time_range = format_time_range(row["start_time"], row["end_time"])
                if time_range:
                    schedule.append({
                        "type": "special",
                        "time": time_range,
                        "ages": row["ages_allowed"] or ""
                    })
                    special_found = True
                    # print(f"SPECIAL HOURS ADDED (range): {time_range} for {row['jump_type']}")
        elif start_date and start_date.date() == target_date.date():
            time_range = format_time_range(row["start_time"], row["end_time"])
            if time_range:
                schedule.append({
                    "type": "special",
                    "time": time_range,
                    "ages": row["ages_allowed"] or ""
                })
                special_found = True
                # print(f"SPECIAL HOURS ADDED (single day): {time_range} for {row['jump_type']}")
    
    # If no special hours for this jump type, get regular hours with overlap adjustment
    if not special_found:
        regular_hours = jump_df[jump_df["hours_type"] == "regular"]
        # print(f"No special hours found for this jump type, checking {len(regular_hours)} regular hours")
        
        for _, row in regular_hours.iterrows():
            start_day = str(row["starting_day_name"]).lower() if row["starting_day_name"] and str(row["starting_day_name"]) != "nan" and not pd.isna(row["starting_day_name"]) else ""
            end_day = str(row["ending_day_name"]).lower() if row["ending_day_name"] and str(row["ending_day_name"]) != "nan" and not pd.isna(row["ending_day_name"]) else ""
            
            # Check if current day falls in the range
            day_in_range = is_day_in_range(day_name, start_day, end_day)
            
            if day_in_range:
                start_time = row["start_time"]
                end_time = row["end_time"]
                
                # Convert times to minutes for easier comparison
                start_minutes = time_to_minutes(start_time)
                end_minutes = time_to_minutes(end_time)
                
                # Check if these regular hours are completely covered by special hours from other jump types
                completely_covered = False
                if all_special_hours:
                    for other_jump_type, special_sessions in all_special_hours.items():
                        for special_session in special_sessions:
                            special_start = special_session["start_minutes"]
                            special_end = special_session["end_minutes"]
                            
                            # Check if regular hours are completely within special hours
                            if start_minutes >= special_start and end_minutes <= special_end:
                                completely_covered = True
                                # print(f"Regular hours {row['jump_type']} ({start_time}-{end_time}) completely covered by {other_jump_type} special hours ({special_session['start_time']}-{special_session['end_time']}) - HIDING")
                                break
                        if completely_covered:
                            break
                
                # If completely covered by special hours, skip these regular hours
                if completely_covered:
                    continue
                
                # Check for partial overlaps with special hours from other jump types
                if all_special_hours:
                    for other_jump_type, special_sessions in all_special_hours.items():
                        for special_session in special_sessions:
                            special_start = special_session["start_minutes"]
                            special_end = special_session["end_minutes"]
                            
                            # Check if there's a partial overlap
                            if not (end_minutes <= special_start or start_minutes >= special_end):
                                # There is an overlap, adjust the regular hours
                                # print(f"Partial overlap: {row['jump_type']} regular ({start_time}-{end_time}) overlaps with {other_jump_type} special ({special_session['start_time']}-{special_session['end_time']})")
                                
                                # Adjust regular end time to special start time if regular starts before special
                                if start_minutes < special_start and end_minutes > special_start:
                                    end_minutes = special_start
                                    end_time = minutes_to_time(end_minutes)
                                    # print(f"Adjusted {row['jump_type']} end time to {end_time}")
                                
                                # Adjust regular start time to special end time if regular ends after special
                                elif start_minutes < special_end and end_minutes > special_end:
                                    start_minutes = special_end
                                    start_time = minutes_to_time(start_minutes)
                                    # print(f"Adjusted {row['jump_type']} start time to {start_time}")
                
                # Apply early closing
                if early_close_time:
                    early_close_minutes = time_to_minutes(early_close_time)
                    
                    if start_minutes < early_close_minutes:
                        end_minutes = min(end_minutes, early_close_minutes)
                        end_time = minutes_to_time(end_minutes)
                    else:
                        continue
                
                # Apply late opening
                if late_open_time:
                    late_open_minutes = time_to_minutes(late_open_time)
                    
                    if end_minutes > late_open_minutes:  # Only adjust if we're opening after the late opening time
                        start_minutes = max(start_minutes, late_open_minutes)
                        start_time = minutes_to_time(start_minutes)
                
                # Only add event if it still has valid time range
                if start_minutes < end_minutes:
                    time_range = format_time_range(start_time, end_time)
                    if time_range:
                        schedule.append({
                            "type": "regular",
                            "time": time_range,
                            "ages": row["ages_allowed"] or ""
                        })
                        # print(f"REGULAR HOURS ADDED: {time_range} for {row['jump_type']}")
    
    return schedule



async def get_events_for_date_async(df: pd.DataFrame, target_date: datetime, current_time: str = None) -> Dict:
    """Get all events and their status for a specific date - async version"""
    def _process_events():
        target_date_str = target_date.strftime("%B %d,%Y")
        day_name = target_date.strftime("%A").lower()
        
        # Convert target_date to naive datetime for comparison
        if hasattr(target_date, 'tzinfo') and target_date.tzinfo is not None:
            target_date_naive = target_date.replace(tzinfo=None)
        else:
            target_date_naive = target_date
        
        result = {
            "status": "open",
            "events": {},
            "notes": []
        }
        
        # DEBUG: Print closed entries for troubleshooting
        # print(f"Processing date: {target_date_naive.date()}")
        closed_entries = df[df["hours_type"] == "closed"]
        # print(f"Found {len(closed_entries)} closed entries")
        
        # Check if location is closed - FIXED LOGIC
        for _, row in closed_entries.iterrows():
            start_date = parse_date(row["starting_date"])
            end_date = parse_date(row["ending_date"])
            
            # print(f"Closed entry: start={start_date}, end={end_date}, target={target_date_naive.date()}")
            
            if start_date and end_date:
                # For date range closure
                if start_date.date() <= target_date_naive.date() <= end_date.date():
                    result["status"] = "closed"
                    reason = row.get("reason", "Operational reasons") or "Operational reasons"
                    result["notes"].append(f"Location closed from {start_date.strftime('%B %d,%Y')} to {end_date.strftime('%B %d,%Y')} - {reason}")
                    result["events"] = {}
                    # print(f"CLOSED: Date in range {start_date.date()} to {end_date.date()}")
                    return result
            elif start_date and start_date.date() == target_date_naive.date():
                # For single day closure
                result["status"] = "closed"
                reason = row.get("reason", "Operational reasons") or "Operational reasons"
                result["notes"].append(f"Location closed on {target_date_str} - {reason}")
                result["events"] = {}
                # print(f"CLOSED: Single day closure on {start_date.date()}")
                return result
        
        # Check for early closing
        early_closing = df[df["hours_type"] == "early_closing"]
        early_close_time = None
        early_close_reason = None
        for _, row in early_closing.iterrows():
            start_date = parse_date(row["starting_date"])
            if start_date and start_date.date() == target_date_naive.date():
                early_close_time = row["end_time"]
                early_close_reason = row.get("reason", "Operational reasons") or "Operational reasons"
                result["notes"].append(f"Early closing at {clean_time(early_close_time)} - {early_close_reason}")
                break
        
        # Check for late opening
        late_opening = df[df["hours_type"] == "late_opening"]
        late_open_time = None
        late_open_reason = None
        for _, row in late_opening.iterrows():
            start_date = parse_date(row["starting_date"])
            if start_date and start_date.date() == target_date_naive.date():
                late_open_time = row["start_time"]
                late_open_reason = row.get("reason", "Operational reasons") or "Operational reasons"
                result["notes"].append(f"Late opening at {clean_time(late_open_time)} - {late_open_reason}")
                break
        
        # Get jump types - only if location is open
        if result["status"] == "open":
            jump_types = df["jump_type"].unique()
            jump_types = [jt for jt in jump_types if jt and str(jt) != "" and str(jt) != "nan" and not pd.isna(jt) and str(jt) != "closed"]
            
            # print(f"Processing jump types for {target_date_naive.date()}: {jump_types}")
            
            # First pass: Collect all special hours to check for overlaps
            all_special_hours = {}
            for jump_type in jump_types:
                jump_df = df[df["jump_type"] == jump_type]
                special_hours = jump_df[jump_df["hours_type"] == "special"]
                
                for _, row in special_hours.iterrows():
                    start_date_special = parse_date(row["starting_date"])
                    end_date_special = parse_date(row["ending_date"])
                    
                    # Check if special hours apply to this date
                    special_applies = False
                    if start_date_special and end_date_special:
                        if start_date_special.date() <= target_date_naive.date() <= end_date_special.date():
                            special_applies = True
                    elif start_date_special and start_date_special.date() == target_date_naive.date():
                        special_applies = True
                    
                    if special_applies:
                        if jump_type not in all_special_hours:
                            all_special_hours[jump_type] = []
                        
                        all_special_hours[jump_type].append({
                            "start_time": row["start_time"],
                            "end_time": row["end_time"],
                            "start_minutes": time_to_minutes(row["start_time"]),
                            "end_minutes": time_to_minutes(row["end_time"])
                        })
            
            # print(f"Found special hours: {all_special_hours}")
            
            # Second pass: Process each jump type with overlap detection
            for jump_type in jump_types:
                jump_df = df[df["jump_type"] == jump_type]
                # print(f"Processing jump_type: {jump_type}, found {len(jump_df)} entries")
                
                # Get event schedule with special hours information for overlap detection
                event_schedule = get_event_schedule_for_date_with_overlaps(
                    jump_df, target_date_naive, day_name, early_close_time, late_open_time, all_special_hours
                )
                
                if event_schedule:
                    result["events"][str(jump_type).replace('_', ' ').title()] = event_schedule
                    # print(f"Added event schedule for {jump_type}: {event_schedule}")
        
        return result
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _process_events)


def get_event_schedule_for_date(jump_df: pd.DataFrame, target_date: datetime, day_name: str, early_close_time: str = None, late_open_time: str = None) -> List[Dict]:
    """Get schedule for a specific jump type on a specific date"""
    schedule = []
    target_date_str = target_date.strftime("%B %d,%Y")
    
    # DEBUG: Print special hours for troubleshooting
    special_hours = jump_df[jump_df["hours_type"] == "special"]
    # print(f"Found {len(special_hours)} special hours for {target_date.date()}")
    
    # Check for special hours first
    special_found = False
    
    for _, row in special_hours.iterrows():
        start_date = parse_date(row["starting_date"])
        end_date = parse_date(row["ending_date"])
        
        # print(f"Special hour: start={start_date}, end={end_date}, target={target_date.date()}, jump_type={row['jump_type']}")
        
        # Check if target date falls within special hours range
        if start_date and end_date:
            if start_date.date() <= target_date.date() <= end_date.date():
                time_range = format_time_range(row["start_time"], row["end_time"])
                if time_range:
                    schedule.append({
                        "type": "special",
                        "time": time_range,
                        "ages": row["ages_allowed"] or ""
                    })
                    special_found = True
                    # print(f"SPECIAL HOURS ADDED (range): {time_range} for {row['jump_type']}")
        elif start_date and start_date.date() == target_date.date():
            time_range = format_time_range(row["start_time"], row["end_time"])
            if time_range:
                schedule.append({
                    "type": "special",
                    "time": time_range,
                    "ages": row["ages_allowed"] or ""
                })
                special_found = True
                # print(f"SPECIAL HOURS ADDED (single day): {time_range} for {row['jump_type']}")
    
    # If no special hours, get regular hours
    if not special_found:
        regular_hours = jump_df[jump_df["hours_type"] == "regular"]
        # print(f"No special hours found, checking {len(regular_hours)} regular hours")
        
        for _, row in regular_hours.iterrows():
            start_day = str(row["starting_day_name"]).lower() if row["starting_day_name"] and str(row["starting_day_name"]) != "nan" and not pd.isna(row["starting_day_name"]) else ""
            end_day = str(row["ending_day_name"]).lower() if row["ending_day_name"] and str(row["ending_day_name"]) != "nan" and not pd.isna(row["ending_day_name"]) else ""
            
            # Check if current day falls in the range
            day_in_range = is_day_in_range(day_name, start_day, end_day)
            
            if day_in_range:
                start_time = row["start_time"]
                end_time = row["end_time"]
                
                # Convert times to minutes for easier comparison
                start_minutes = time_to_minutes(start_time)
                end_minutes = time_to_minutes(end_time)
                
                # Apply early closing
                if early_close_time:
                    early_close_minutes = time_to_minutes(early_close_time)
                    
                    if start_minutes < early_close_minutes:
                        end_minutes = min(end_minutes, early_close_minutes)
                        end_time = minutes_to_time(end_minutes)
                    else:
                        continue
                
                # Apply late opening
                if late_open_time:
                    late_open_minutes = time_to_minutes(late_open_time)
                    
                    if end_minutes > late_open_minutes:  # Only adjust if we're opening after the late opening time
                        start_minutes = max(start_minutes, late_open_minutes)
                        start_time = minutes_to_time(start_minutes)
                
                # Only add event if it still has valid time range
                if start_minutes < end_minutes:
                    time_range = format_time_range(start_time, end_time)
                    if time_range:
                        schedule.append({
                            "type": "regular",
                            "time": time_range,
                            "ages": row["ages_allowed"] or ""
                        })
                        # print(f"REGULAR HOURS ADDED: {time_range} for {row['jump_type']}")
    
    return schedule



def is_day_in_range(target_day: str, start_day: str, end_day: str) -> bool:
    """Check if target day falls within the day range"""
    if not start_day:
        return False
    
    days_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    try:
        target_idx = days_order.index(target_day.lower())
        start_idx = days_order.index(start_day.lower())
        
        if not end_day or start_day.lower() == end_day.lower():
            return target_idx == start_idx
        
        end_idx = days_order.index(end_day.lower())
        
        if end_idx >= start_idx:
            return start_idx <= target_idx <= end_idx
        else:
            # Wrap around case (e.g., Friday to Monday)
            return target_idx >= start_idx or target_idx <= end_idx
            
    except ValueError:
        return False

async def get_future_special_events_async(df: pd.DataFrame, start_date: datetime) -> List[Dict]:
    """Get future special hours events (excluding those in the 7-day range) - async version"""
    # print("get_future_special_events_async called" , df)
    # print('test 1')
    if df.empty:
        # print('test 2')
        return []
    def _process_special_events():
        special_events = []

        special_hours = df[df["hours_type"] == "special"]
        # print("get_future_special_events_async called")
        # print("This is the special hours df:", special_hours)
        # print("get_future_special_events_async called after")

        
        # Convert start_date to naive for comparison
        if hasattr(start_date, 'tzinfo') and start_date.tzinfo is not None:
            start_date_naive = start_date.replace(tzinfo=None)
        else:
            start_date_naive = start_date
        
        seven_day_end = start_date_naive + timedelta(days=6)
        
        for _, row in special_hours.iterrows():
            start_date_obj = parse_date(row["starting_date"])
            end_date_obj = parse_date(row["ending_date"])
            
            if start_date_obj:
                if start_date_obj.date() > seven_day_end.date():
                    time_range = format_time_range(row["start_time"], row["end_time"])
                    jump_type = str(row["jump_type"]).replace('_', ' ').title() if row["jump_type"] else ""
                    
                    event_info = {
                        "jump_type": jump_type,
                        "start_date": start_date_obj.strftime("%A, %B %d, %Y"),
                        "time": time_range,
                        "ages": row["ages_allowed"] or ""
                    }
                    
                    if end_date_obj and end_date_obj != start_date_obj:
                        event_info["end_date"] = end_date_obj.strftime("%A, %B %d, %Y")
                    
                    special_events.append(event_info)
        
        return sorted(special_events, key=lambda x: parse_date(x["start_date"].split(", ", 1)[1] if x["start_date"] else datetime.min))
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _process_special_events)

async def get_future_closures_async(df: pd.DataFrame, start_date: datetime) -> List[Dict]:
    # print("get_future_closures_async called" , df)
    # print("get_future_closures_async called" , start_date)
    """Get future closure dates (excluding those in the 7-day range) - async version"""
    # print('test 1')
    if df.empty:
        # print('test 2')
        return []
    def _process_closures():
        closures = []
        closed_entries = df[df["hours_type"] == "closed"]
        # print("Closed entries:", closed_entries)
        
        # Convert start_date to naive for comparison
        if hasattr(start_date, 'tzinfo') and start_date.tzinfo is not None:
            start_date_naive = start_date.replace(tzinfo=None)
        else:
            start_date_naive = start_date
        
        seven_day_end = start_date_naive + timedelta(days=6)
        
        for _, row in closed_entries.iterrows():
            start_date_obj = parse_date(row["starting_date"])
            end_date_obj = parse_date(row["ending_date"])
            
            if start_date_obj:
                if start_date_obj.date() > seven_day_end.date():
                    closure_info = {
                        "start_date": start_date_obj.strftime("%A, %B %d, %Y")
                    }
                    
                    if end_date_obj and end_date_obj != start_date_obj:
                        closure_info["end_date"] = end_date_obj.strftime("%A, %B %d, %Y")
                    
                    closures.append(closure_info)
                    # print("Added closure:", closure_info)
        
        return sorted(closures, key=lambda x: parse_date(x["start_date"].split(", ", 1)[1] if x["start_date"] else datetime.min))
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _process_closures)

async def get_future_early_closings_async(df: pd.DataFrame, start_date: datetime) -> List[Dict]:
    """Get future early closing dates (excluding those in the 7-day range) - async version"""

    def _process_early_closings():
        early_closings = []
        early_entries = df[df["hours_type"] == "early_closing"]
        
        # Convert start_date to naive for comparison
        if hasattr(start_date, 'tzinfo') and start_date.tzinfo is not None:
            start_date_naive = start_date.replace(tzinfo=None)
        else:
            start_date_naive = start_date
        
        seven_day_end = start_date_naive + timedelta(days=6)
        
        for _, row in early_entries.iterrows():
            closure_date = parse_date(row["starting_date"])
            
            if closure_date:
                if closure_date.date() > seven_day_end.date():
                    early_closings.append({
                        "date": closure_date.strftime("%A, %B %d, %Y"),
                        "time": clean_time(row["end_time"]),
                        "reason": row.get("reason", "Operational reasons") or "Operational reasons"
                    })
        
        return sorted(early_closings, key=lambda x: parse_date(x["date"].split(", ", 1)[1] if x["date"] else datetime.min))
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _process_early_closings)

async def get_future_late_openings_async(df: pd.DataFrame, start_date: datetime) -> List[Dict]:
    """Get future late opening dates (excluding those in the 7-day range) - async version"""
    def _process_late_openings():
        late_openings = []
        late_entries = df[df["hours_type"] == "late_opening"]
        
        # Convert start_date to naive for comparison
        if hasattr(start_date, 'tzinfo') and start_date.tzinfo is not None:
            start_date_naive = start_date.replace(tzinfo=None)
        else:
            start_date_naive = start_date
        
        seven_day_end = start_date_naive + timedelta(days=6)
        
        for _, row in late_entries.iterrows():
            opening_date = parse_date(row["starting_date"])
            
            if opening_date:
                if opening_date.date() > seven_day_end.date():
                    late_openings.append({
                        "date": opening_date.strftime("%A, %B %d, %Y"),
                        "time": clean_time(row["start_time"]),
                        "reason": row.get("reason", "Operational reasons") or "Operational reasons"
                    })
        
        return sorted(late_openings, key=lambda x: parse_date(x["date"].split(", ", 1)[1] if x["date"] else datetime.min))
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _process_late_openings)



async def get_future_regular_schedule_async(hours_df: pd.DataFrame) -> Dict:
    
    def _process_regular_schedule():
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        regular_hours = hours_df[hours_df["hours_type"] == "regular"]
        future_regular_schedule = {}
        
        for day in days_of_week:
            day_events = {}
            jump_types = hours_df["jump_type"].unique()
            jump_types = [jt for jt in jump_types if jt and str(jt) != "" and str(jt) != "nan" and not pd.isna(jt)]
            
            for jump_type in jump_types:

                jump_df = regular_hours[regular_hours["jump_type"] == jump_type]
                
                for _, row in jump_df.iterrows():
                    start_day = str(row["starting_day_name"]).lower() if row["starting_day_name"] and not pd.isna(row["starting_day_name"]) else ""
                    end_day = str(row["ending_day_name"]).lower() if row["ending_day_name"] and not pd.isna(row["ending_day_name"]) else ""
                    
                    if is_day_in_range(day.lower(), start_day, end_day):
                        time_range = format_time_range(row["start_time"], row["end_time"])
                        if time_range:
                            jump_type_title = str(jump_type).replace('_', ' ').title()
                            if jump_type_title not in day_events:
                                day_events[jump_type_title] = []
                            
                            day_events[jump_type_title].append({
                                "time": time_range,
                                "ages": row["ages_allowed"] or ""
                                
                            })
            
            if day_events:
                future_regular_schedule[day] = day_events
        
        return future_regular_schedule
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _process_regular_schedule)
    

async def process_comprehensive_schedule(location_id: int, timezone: str) -> Dict:
    """
    Process the hours dataframe to create comprehensive schedule information - optimized async version
    """
    # Get data from database instead of Google Sheets
    hours_df = await get_hours_data_from_db(location_id)
    
    # Clean the dataframe
    hours_df = hours_df.astype(str).apply(lambda x: x.str.strip())
    hours_df.replace(["nan", ""], "", inplace=True)
    
    # print('test 1')
    if hours_df.empty:
        # print('test 2')
        return {"status": "No data available"}
    # Get current California time
    california_time = await get_california_time(timezone)
    current_date = california_time.date()
    current_time = california_time.strftime("%I:%M %p")
    current_day_name = california_time.strftime("%A")
    human_readable_date = california_time.strftime("%d %B, %Y")
    
    # Calculate the end date for the 7-day range
    end_date = california_time + timedelta(days=6)
    end_date_str = end_date.strftime("%B %d, %Y")
    end_day_name = end_date.strftime("%A")
    
    # Initialize result structure
    schedule_result = {
        "current_info": {
            "current_date": f"{current_date} ({human_readable_date})",
            "current_time": current_time,
            "current_day": current_day_name,
            "seven_day_range": f"{current_day_name} {human_readable_date} to {end_day_name} {end_date_str}"
        },
        "seven_day_schedule": {},
        "future_regular_schedule": {},
        "future_special_hours": [],
        "future_closures": [],
        "future_early_closings": [],
        "future_late_openings": []
    }
    
    # Get next 7 days and process all future items concurrently
    seven_days_task = get_next_seven_days_async(california_time)
    future_tasks = [
        get_future_special_events_async(hours_df, california_time),
        get_future_closures_async(hours_df, california_time),
        get_future_early_closings_async(hours_df, california_time),
        get_future_late_openings_async(hours_df, california_time),
        get_future_regular_schedule_async(hours_df)
    ]
    
    # Wait for seven days calculation and future items
    seven_days, future_results = await asyncio.gather(
        seven_days_task,
        asyncio.gather(*future_tasks)
    )
    
    # Unpack future results
    (schedule_result["future_special_hours"], 
     schedule_result["future_closures"], 
     schedule_result["future_early_closings"], 
     schedule_result["future_late_openings"],
     schedule_result["future_regular_schedule"]) = future_results
    
    # Process seven day schedule concurrently
    seven_day_tasks = []
    for day_name, formatted_date, date_obj in seven_days:
        seven_day_tasks.append(get_events_for_date_async(hours_df, date_obj, current_time))
    
    seven_day_results = await asyncio.gather(*seven_day_tasks)
    
    # Build seven day schedule result
    for i, (day_name, formatted_date, date_obj) in enumerate(seven_days):
        schedule_result["seven_day_schedule"][f"{day_name} ({formatted_date})"] = seven_day_results[i]
    
    return schedule_result


async def format_schedule_for_display(schedule_data: Dict) -> str:
    """Format the schedule data for easy reading - async version"""
    def _format_output():
        output_lines = []
        output_lines.append("""
#### Step 1: Identify Day
- Ask: "What day are you hoping to bounce with us?" (if not mentioned)
- For dates mentioned, convert to day name using `identify_day_name_from_date(YYYY-mm-dd)`
#### Step 2: Check Closures FIRST
- **For TODAY:** Check if 2025-12-10 ( 10 December, 2025 ) is closed
- **For FUTURE:** Calculate actual date from 2025-12-10 ( 10 December, 2025 ), then check closures
- **If closed:** Express regret, offer alternatives
- **If open:** Continue
#### Step 3: Determine Available Programs
- Only mention programs scheduled for that specific day
- Check: Open Jump, Glow, Little Leaper
#### Step 4: Provide Hours (**Special Hours Priority**)
- **PRIORITY:** Check special hours for the calculated date FIRST
- **If special hours exist:** Provide ONLY special hours (don't mention regular)
- **If no special hours:** Provide regular hours
- Only list programs available that day
#### Step 5: Present Discounts
- Check discount data for the day
- If no day restriction mentioned, apply to all weekdays
#### Step 6: Discover Purpose
- Ask: "Are you planning jump passes or celebrating something special like a birthday?"
- Respond appropriately based on answer
**Schedule Reference:**""")    
        # Current info
        output_lines.append("=== CURRENT INFORMATION ===")
        current = schedule_data["current_info"]
        output_lines.append(f"Today Date: {current['current_date']}")
        output_lines.append(f"Current Time (Today): {current['current_time']}")
        output_lines.append(f"Today Day Name: {current['current_day']}")
        output_lines.append(f"7-Day Schedule Range: {current['seven_day_range']}")
        output_lines.append("")
        
        # Next 7 days schedule
        output_lines.append("=== NEXT 7 DAYS SCHEDULE ===")

        for date_key, day_data in schedule_data["seven_day_schedule"].items():
            output_lines.append(f"\n{date_key}:")
            
            if day_data["status"] == "closed":
                output_lines.append("  LOCATION CLOSED")
                if day_data["notes"]:
                    for note in day_data["notes"]:
                        output_lines.append(f"  {note}")
            else:
                if day_data["events"]:
                    for event_type, sessions in day_data["events"].items():
                        has_special = any(session.get("type") == "special" for session in sessions)
                        event_label = f"{event_type} (Special Hours)" if has_special else event_type
                        
                        output_lines.append(f"  {event_label}:")
                        for session in sessions:
                            output_lines.append(f"    {session['time']} - {session['ages']}")
                else:
                    output_lines.append("  No events scheduled")
            
            if day_data["notes"]:
                for note in day_data["notes"]:
                    output_lines.append(f"  NOTE: {note}")
        
        # Future regular schedule
        if schedule_data["future_regular_schedule"]:
            output_lines.append("\n\n=== REGULAR WEEKLY SCHEDULE ===")
            for day, events in schedule_data["future_regular_schedule"].items():
                output_lines.append(f"\n{day}:")
                for event_type, sessions in events.items():
                    output_lines.append(f"  {event_type}:")
                    for session in sessions:
                        output_lines.append(f"    {session['time']} - {session['ages']}")
        
        # Future special events
        if schedule_data["future_special_hours"]:
            output_lines.append("\n\n=== FUTURE SPECIAL HOURS ===")
            for event in schedule_data["future_special_hours"]:
                date_range = event["start_date"]
                if "end_date" in event:
                    date_range += f" to {event['end_date']}"
                output_lines.append(f"  {event['jump_type']} (Special Hours): {date_range} - {event['time']} ({event['ages']})")
        
        # Future closures
        if schedule_data["future_closures"]:
            output_lines.append("\n\n=== FUTURE CLOSURES ===")
            for closure in schedule_data["future_closures"]:
                date_range = closure["start_date"]
                if "end_date" in closure:
                    date_range += f" to {closure['end_date']}"
                output_lines.append(f"  CLOSED: {date_range}")
        
        # Future early closings
        if schedule_data["future_early_closings"]:
            output_lines.append("\n\n=== FUTURE EARLY CLOSINGS ===")
            for early in schedule_data["future_early_closings"]:
                output_lines.append(f"  {early['date']}: Closing early at {early['time']} - {early['reason']}")
        
        # Future late openings
        if schedule_data["future_late_openings"]:
            output_lines.append("\n\n=== FUTURE LATE OPENINGS ===")
            for late in schedule_data["future_late_openings"]:
                output_lines.append(f"  {late['date']}: Opening late at {late['time']} - {late['reason']}")
        

        output_lines.append("""
**Discounts:**
- a 15% discount is available for military personnel and first responders, valid on tickets and parties only..
- get 15% off when booking a party through the app from monday to thursday using the code 10-b-day-week.
elite members receive 20% off on party bookings.
**Critical Rules:**
- ALWAYS check closures first for the specific calculated date
- CALCULATE actual dates for future day requests from 2025-12-08 ( 08 December, 2025 )
- Special hours override regular hours completely
- Never mention unavailable programs
- Always ask about visit purpose
### End of Hours of Operation Inquiry Process ###
        """)
        return "\n".join(output_lines)
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _format_output)


# Main function to get hours of operation info
async def get_hours_of_operation_info(location_id: int, timezone: str) -> str:
    """
    Main function to get formatted hours of operation information
    """
    schedule_data = await process_comprehensive_schedule(location_id, timezone)
    if "status" in schedule_data and schedule_data["status"] == "No data available":
        return "No hours of operation data available for this location."
    formatted_output = await format_schedule_for_display(schedule_data)
    return formatted_output




