import pandas as pd
from typing import Dict
from contextvars import ContextVar
from typing import Dict, Optional
from collections import defaultdict
import asyncio
from datetime import datetime, timedelta
import aiohttp
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import pytz
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools
import re
import aiofiles
import os
from zoneinfo import ZoneInfo
import re
import time
import gc
import uuid
import traceback
# Add connection pooling and session reuse
_http_session = None

async def get_http_session():
    """Get or create a shared HTTP session for connection pooling"""
    global _http_session
    if _http_session is None or _http_session.closed:
        connector = aiohttp.TCPConnector(
            limit=20,  # Total connection limit
            limit_per_host=10,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
        )
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        _http_session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
    return _http_session
async def get_california_time(timezone):
    """Get current California time"""
    california_tz = pytz.timezone(timezone)
    return datetime.now(california_tz)


# Clean and validate each field 
def is_valid(val):
    return (
        pd.notna(val)
        and str(val).strip() != ""
        and str(val).lower().strip() != "nan"
    )

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object (timezone-naive)"""
    if not date_str or date_str.lower() in ["nan", "none", ""]:
        return None

    # Try multiple known formats
    for fmt in ("%Y-%m-%d", "%B %d,%Y", "%B %d, %Y", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

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
    t = str(t).strip().lower().replace('.', '')
    if not t:
        return t

    parts = t.split(':')
    hour = parts[0].lstrip('0') or '0'

    # if AM/PM is present
    if len(parts) > 1 and ' ' in parts[1]:
        minute, am_pm = parts[1].split(' ', 1)
    else:
        minute = parts[1] if len(parts) > 1 else '00'
        am_pm = ''

    # remove seconds if present (e.g., 09:00:00)
    if len(parts) > 2:
        minute = parts[1]

    if minute == '00':
        result = f"{hour} {am_pm}".strip()
        return result
    result = f"{hour}:{minute} {am_pm}".strip()
    return result


def format_time_range(start_time: str, end_time: str) -> str:
    if start_time and end_time:
        return f"{clean_time(start_time)} to {clean_time(end_time)}"
    return ""

def time_to_minutes(time_str: str) -> int:
    """Convert time string to minutes since midnight for comparison"""
    if not time_str:
        return 0
    try:
        time_obj = datetime.strptime(time_str, "%I:%M %p")
        return time_obj.hour * 60 + time_obj.minute
    except:
        try:
            time_obj = datetime.strptime(time_str, "%I %p")
            return time_obj.hour * 60
        except:
            try:
                time_str_clean = time_str.replace(' ', '').upper()
                if 'AM' in time_str_clean or 'PM' in time_str_clean:
                    hour_str = time_str_clean.replace('AM', '').replace('PM', '')
                    hour = int(hour_str)
                    if 'PM' in time_str_clean and hour != 12:
                        hour += 12
                    elif 'AM' in time_str_clean and hour == 12:
                        hour = 0
                    return hour * 60
            except:
                return 0
    return 0

def minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight back to time string"""
    hours = minutes // 60
    mins = minutes % 60
    time_obj = datetime.strptime(f"{hours:02d}:{mins:02d}", "%H:%M")
    return time_obj.strftime("%I:%M %p")


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
        
        # Check if location is closed
        closed_entries = df[df["hours_type"] == "closed"]
        for _, row in closed_entries.iterrows():
            start_date = parse_date(row["starting_date"])
            end_date = parse_date(row["ending_date"])
            
            if start_date and end_date:
                if start_date <= target_date_naive <= end_date:
                    result["status"] = "closed"
                    reason = row.get("reason", "Operational reasons")
                    result["notes"].append(f"Location closed from {start_date.strftime('%B %d,%Y')} to {end_date.strftime('%B %d,%Y')} - {reason}")
                    result["events"] = {}
                    result["closure_reason"] = reason
                    return result
            elif start_date and start_date.date() == target_date_naive.date():
                result["status"] = "closed"
                reason = row.get("reason", "Operational reasons")
                result["notes"].append(f"Location closed on {target_date_str} - {reason}")
                result["events"] = {}
                result["closure_reason"] = reason
                return result
        
        # Check for early closing
        early_closing = df[df["hours_type"] == "early_closing"]
        early_close_time = None
        early_close_reason = None
        for _, row in early_closing.iterrows():
            start_date = parse_date(row["starting_date"])
            if start_date and start_date.date() == target_date_naive.date():
                early_close_time = row["end_time"]
                early_close_reason = row.get("reason", "Operational reasons")
                result["notes"].append(f"Early closing at {early_close_time} - {early_close_reason}")
                result["early_close_reason"] = early_close_reason
                break
        
        # Check for late opening
        late_opening = df[df["hours_type"] == "late_opening"]
        late_open_time = None
        late_open_reason = None
        for _, row in late_opening.iterrows():
            start_date = parse_date(row["starting_date"])
            if start_date and start_date.date() == target_date_naive.date():
                late_open_time = row["start_time"]
                late_open_reason = row.get("reason", "Operational reasons")
                result["notes"].append(f"Late opening at {late_open_time} - {late_open_reason}")
                result["late_open_reason"] = late_open_reason
                break
        
        # Get jump types
        jump_types = df["jump_type"].unique()
        jump_types = [jt for jt in jump_types if jt and jt != "" and jt != "nan"]
        
        for jump_type in jump_types:
            jump_df = df[df["jump_type"] == jump_type]
            event_schedule = get_event_schedule_for_date(jump_df, target_date_naive, day_name, early_close_time, late_open_time)
            if event_schedule:
                result["events"][jump_type.replace('_', ' ').title()] = event_schedule
        
        return result
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _process_events)

def get_event_schedule_for_date(jump_df: pd.DataFrame, target_date: datetime, day_name: str, early_close_time: str = None, late_open_time: str = None) -> List[Dict]:
    """Get schedule for a specific jump type on a specific date"""
    schedule = []
    target_date_str = target_date.strftime("%B %d,%Y")
    
    # Check for special hours first
    special_hours = jump_df[jump_df["hours_type"] == "special"]
    special_found = False
    
    for _, row in special_hours.iterrows():
        start_date = parse_date(row["starting_date"])
        end_date = parse_date(row["ending_date"])
        
        # Check if target date falls within special hours range
        if start_date and end_date:
            if start_date <= target_date <= end_date:
                time_range = format_time_range(row["start_time"], row["end_time"])
                if time_range:
                    schedule.append({
                        "type": "special",
                        "time": time_range,
                        "ages": row["ages_allowed"]
                    })
                    special_found = True
        elif start_date and start_date.date() == target_date.date():
            time_range = format_time_range(row["start_time"], row["end_time"])
            if time_range:
                schedule.append({
                    "type": "special",
                    "time": time_range,
                    "ages": row["ages_allowed"]
                })
                special_found = True
    
    # If no special hours, get regular hours
    if not special_found:
        regular_hours = jump_df[jump_df["hours_type"] == "regular"]
        
        for _, row in regular_hours.iterrows():
            start_day = row["starting_day_name"].lower() if row["starting_day_name"] and row["starting_day_name"] != "nan" else ""
            end_day = row["ending_day_name"].lower() if row["ending_day_name"] and row["ending_day_name"] != "nan" else ""
            
            
            # Check if current day falls in the range
            if is_day_in_range(day_name, start_day, end_day):
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
                    
                    if start_minutes < late_open_minutes:
                        start_minutes = max(start_minutes, late_open_minutes)
                        start_time = minutes_to_time(start_minutes)
                
                # Only add event if it still has valid time range
                if start_minutes < end_minutes:
                    time_range = format_time_range(start_time, end_time)
                    if time_range:
                        schedule.append({
                            "type": "regular",
                            "time": time_range,
                            "ages": row["ages_allowed"]
                        })
    
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


async def get_all_future_affected_dates_async(df: pd.DataFrame, start_date: datetime) -> List[Dict]:
    """Get ALL future dates (from today onwards) that have special events, closures, or modifications"""
    def _process_affected_dates():
        affected_dates = []
        
        # Convert start_date to naive for comparison
        if hasattr(start_date, 'tzinfo') and start_date.tzinfo is not None:
            start_date_naive = start_date.replace(tzinfo=None)
        else:
            start_date_naive = start_date
        
        # Process special hours
        special_hours = df[df["hours_type"] == "special"]
        for _, row in special_hours.iterrows():
            start_date_obj = parse_date(row["starting_date"])
            end_date_obj = parse_date(row["ending_date"])
            
            if start_date_obj and start_date_obj.date() >= start_date_naive.date():
                time_range = format_time_range(row["start_time"], row["end_time"])
                jump_type = row["jump_type"].replace('_', ' ').title() if row["jump_type"] else ""
                
                if end_date_obj and end_date_obj != start_date_obj:
                    # Add all dates in range
                    current = start_date_obj
                    while current <= end_date_obj:
                        affected_dates.append({
                            "type": "special_hours",
                            "date_obj": current,
                            "jump_type": jump_type,
                            "time": time_range,
                            "ages": row["ages_allowed"]
                        })
                        current += timedelta(days=1)
                else:
                    affected_dates.append({
                        "type": "special_hours",
                        "date_obj": start_date_obj,
                        "jump_type": jump_type,
                        "time": time_range,
                        "ages": row["ages_allowed"]
                    })
        
        # Process closures
        closed_entries = df[df["hours_type"] == "closed"]
        for _, row in closed_entries.iterrows():
            start_date_obj = parse_date(row["starting_date"])
            end_date_obj = parse_date(row["ending_date"])
            reason = row.get("reason", "Operational reasons")
            
            if start_date_obj and start_date_obj.date() >= start_date_naive.date():
                if end_date_obj and end_date_obj != start_date_obj:
                    current = start_date_obj
                    while current <= end_date_obj:
                        affected_dates.append({
                            "type": "closure",
                            "date_obj": current,
                            "reason": reason
                        })
                        current += timedelta(days=1)
                else:
                    affected_dates.append({
                        "type": "closure",
                        "date_obj": start_date_obj,
                        "reason": reason
                    })
        
        # Process early closings
        early_entries = df[df["hours_type"] == "early_closing"]
        for _, row in early_entries.iterrows():
            closure_date = parse_date(row["starting_date"])
            
            if closure_date and closure_date.date() >= start_date_naive.date():
                affected_dates.append({
                    "type": "early_closing",
                    "date_obj": closure_date,
                    "time": row["end_time"],
                    "reason": row.get("reason", "Operational reasons")
                })
        
        # Process late openings
        late_entries = df[df["hours_type"] == "late_opening"]
        for _, row in late_entries.iterrows():
            opening_date = parse_date(row["starting_date"])
            
            if opening_date and opening_date.date() >= start_date_naive.date():
                affected_dates.append({
                    "type": "late_opening",
                    "date_obj": opening_date,
                    "time": row["start_time"],
                    "reason": row.get("reason", "Operational reasons")
                })
        
        # Sort by date
        affected_dates.sort(key=lambda x: x["date_obj"])
        
        return affected_dates
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _process_affected_dates)


async def get_future_regular_schedule_async(hours_df: pd.DataFrame) -> Dict:
    """Process future regular schedule (general weekly pattern) - async version"""
    def _process_regular_schedule():
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        regular_hours = hours_df[hours_df["hours_type"] == "regular"]
        future_regular_schedule = {}
        
        for day in days_of_week:
            day_events = {}
            jump_types = hours_df["jump_type"].unique()
            jump_types = [jt for jt in jump_types if jt and jt != "" and jt != "nan"]
            
            for jump_type in jump_types:
                jump_df = regular_hours[regular_hours["jump_type"] == jump_type]
                
                for _, row in jump_df.iterrows():
                    start_day = row["starting_day_name"].lower() if row["starting_day_name"] else ""
                    end_day = row["ending_day_name"].lower() if row["ending_day_name"] else ""
                    
                    if is_day_in_range(day.lower(), start_day, end_day):
                        time_range = format_time_range(row["start_time"], row["end_time"])
                        if time_range:
                            if jump_type.replace('_', ' ').title() not in day_events:
                                day_events[jump_type.replace('_', ' ').title()] = []
                            
                            day_events[jump_type.replace('_', ' ').title()].append({
                                "time": time_range,
                                "ages": row["ages_allowed"]
                            })
            
            if day_events:
                future_regular_schedule[day] = day_events
        
        return future_regular_schedule
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _process_regular_schedule)

async def process_comprehensive_schedule(hours_df: pd.DataFrame, timezone: str) -> Dict:
    """
    Process the hours dataframe to create comprehensive schedule information - optimized async version
    """
    # Clean the dataframe
    hours_df = hours_df.astype(str).apply(lambda x: x.str.strip())
    hours_df.replace(["nan", ""], "", inplace=True)
    hours_df['start_time'] = pd.to_datetime(hours_df['start_time'], format='%H:%M:%S').dt.strftime('%I:%M %p')
    hours_df['end_time'] = pd.to_datetime(hours_df['end_time'], format='%H:%M:%S').dt.strftime('%I:%M %p')
    
    hours_df['start_time'] = hours_df['start_time'].str.replace(r':00(?=\s[AP]M)', '', regex=True)
    hours_df['end_time'] = hours_df['end_time'].str.replace(r':00(?=\s[AP]M)', '', regex=True)
    
    # Start getting California time asynchronously using create_task
    california_time_task = asyncio.create_task(get_california_time(timezone))
    
    # Start processing affected dates and regular schedule concurrently
    # We'll await california_time first since we need it for affected_dates
    california_time = await california_time_task
    
    current_date = california_time.date()
    current_time = california_time.strftime("%I:%M %p")
    current_day_name = california_time.strftime("%A")
    human_readable_date = california_time.strftime("%d %B, %Y")
    
    # Now create tasks for affected dates and regular schedule
    affected_dates_task = asyncio.create_task(get_all_future_affected_dates_async(hours_df, california_time))
    regular_schedule_task = asyncio.create_task(get_future_regular_schedule_async(hours_df))
    
    # Initialize result structure
    schedule_result = {
        "current_info": {
            "current_date": f"{current_date} ({human_readable_date})",
            "current_time": current_time,
            "current_day": current_day_name
        },
        "affected_dates": [],
        "future_regular_schedule": {}
    }
    
    # Wait for both tasks to complete
    schedule_result["affected_dates"], schedule_result["future_regular_schedule"] = await asyncio.gather(
        affected_dates_task,
        regular_schedule_task
    )
    
    return schedule_result


async def build_schedule_for_date(date_key: str, events_list: List[Dict], regular_schedule: Dict) -> Dict:
    """Build complete schedule for a date using regular hours + modifications"""
    day_name = date_key.split(" (")[0]  # Extract day name like "Wednesday"
    
    result = {
        "status": "open",
        "events": {},
        "notes": []
    }
    
    # Check if any event is a closure
    for event_data in events_list:
        if event_data["type"] == "closure":
            result["status"] = "closed"
            reason = event_data.get("reason", "Operational reasons")
            result["notes"].append(f"Location closed - {reason}")
            result["closure_reason"] = reason
            return result
    
    # Get early closing and late opening times
    early_close_time = None
    early_close_reason = None
    late_open_time = None
    late_open_reason = None
    
    for event_data in events_list:
        if event_data["type"] == "early_closing":
            early_close_time = event_data["time"]
            early_close_reason = event_data.get("reason", "Operational reasons")
        elif event_data["type"] == "late_opening":
            late_open_time = event_data["time"]
            late_open_reason = event_data.get("reason", "Operational reasons")
    
    # Start with regular hours for this day
    if day_name in regular_schedule:
        result["events"] = {}
        for jump_type, sessions in regular_schedule[day_name].items():
            result["events"][jump_type] = []
            for session in sessions:
                result["events"][jump_type].append({
                    "type": "regular",
                    "time": session["time"],
                    "ages": session["ages"]
                })
    
    # Apply special hours (these override regular hours)
    for event_data in events_list:
        if event_data["type"] == "special_hours":
            jump_type = event_data["jump_type"]
            result["events"][jump_type] = [{
                "type": "special",
                "time": event_data["time"],
                "ages": event_data["ages"]
            }]
            result["notes"].append(f"{jump_type} has special hours on this date")
    
    # Apply early closing and late opening adjustments to all events
    if early_close_time or late_open_time:
        adjusted_events = {}
        
        for jump_type, sessions in result["events"].items():
            adjusted_sessions = []
            
            for session in sessions:
                time_range = session["time"]
                # Parse time range (e.g., "9 am to 10 am")
                try:
                    start_str, end_str = time_range.split(" to ")
                    
                    start_minutes = time_to_minutes(start_str.strip())
                    end_minutes = time_to_minutes(end_str.strip())
                    
                    # Apply early closing
                    if early_close_time:
                        early_close_minutes = time_to_minutes(early_close_time)
                        
                        # If event starts at or after early closing, skip it entirely
                        if start_minutes >= early_close_minutes:
                            continue
                        
                        # If event ends after early closing, adjust end time
                        if end_minutes > early_close_minutes:
                            end_minutes = early_close_minutes
                    
                    # Apply late opening
                    if late_open_time:
                        late_open_minutes = time_to_minutes(late_open_time)
                        
                        # If event ends at or before late opening, skip it entirely
                        if end_minutes <= late_open_minutes:
                            continue
                        
                        # If event starts before late opening, adjust start time
                        if start_minutes < late_open_minutes:
                            start_minutes = late_open_minutes
                    
                    # Only add if there's still a valid time range
                    if start_minutes < end_minutes:
                        adjusted_time = format_time_range(
                            minutes_to_time(start_minutes),
                            minutes_to_time(end_minutes)
                        )
                        adjusted_sessions.append({
                            "type": session["type"],
                            "time": adjusted_time,
                            "ages": session["ages"]
                        })
                except:
                    # If parsing fails, keep original
                    adjusted_sessions.append(session)
            
            if adjusted_sessions:
                adjusted_events[jump_type] = adjusted_sessions
        
        result["events"] = adjusted_events
    
    # Add notes about early closing and late opening
    if early_close_time:
        result["notes"].append(f"Early closing at {early_close_time} - {early_close_reason}")
        result["early_close_reason"] = early_close_reason
    
    if late_open_time:
        result["notes"].append(f"Late opening at {late_open_time} - {late_open_reason}")
        result["late_open_reason"] = late_open_reason
    
    return result


async def format_schedule_for_display(schedule_data: Dict) -> str:
    """Format the schedule data showing all events with regular hours as baseline"""
    output_lines = []
    
    # Current info
    output_lines.append("=== CURRENT INFORMATION ===")
    current = schedule_data["current_info"]
    output_lines.append(f"Today Date: {current['current_date']}")
    output_lines.append(f"Current Time (Today): {current['current_time']}")
    output_lines.append(f"Today Day Name: {current['current_day']}")
    output_lines.append("")
    
    # Get all affected dates
    affected_dates = schedule_data.get("affected_dates", [])
    
    # If we have affected dates, show complete schedule
    if affected_dates:
        output_lines.append("=== SCHEDULE WITH SPECIAL EVENTS/MODIFICATIONS ===")
        output_lines.append("(Showing all future dates with closures, special hours, early closings, or late openings)")
        
        # Get regular schedule for reference
        regular_schedule = schedule_data.get("future_regular_schedule", {})
        
        # Group events by date to handle multiple events on same date
        date_events = {}
        for event_data in affected_dates:
            date_obj = event_data["date_obj"]
            day_name = date_obj.strftime("%A")
            formatted_date = date_obj.strftime("%B %d, %Y")
            date_key = f"{day_name} ({formatted_date})"
            
            if date_key not in date_events:
                date_events[date_key] = []
            date_events[date_key].append(event_data)
        
        # Build schedule for all dates concurrently using create_task
        schedule_tasks = []
        date_keys_ordered = list(date_events.keys())
        
        for date_key in date_keys_ordered:
            events = date_events[date_key]
            task = asyncio.create_task(build_schedule_for_date(date_key, events, regular_schedule))
            schedule_tasks.append(task)
        
        # Wait for all schedules to be built concurrently
        day_schedules = await asyncio.gather(*schedule_tasks)
        
        # Now format the output with the results
        for i, date_key in enumerate(date_keys_ordered):
            day_schedule = day_schedules[i]
            
            output_lines.append(f"\n{date_key}:")
            
            if day_schedule["status"] == "closed":
                # Show closure with reason
                for note in day_schedule.get("notes", []):
                    if note:
                        output_lines.append(f"  {note}")
            else:
                if day_schedule["events"]:
                    for event_type, sessions in day_schedule["events"].items():
                        has_special = any(session.get("type") == "special" for session in sessions)
                        event_label = f"{event_type} (Special Hours)" if has_special else event_type
                        
                        output_lines.append(f"  {event_label}:")
                        for session in sessions:
                            output_lines.append(f"    {session['time']} - {session['ages']}")
                else:
                    output_lines.append("  No events scheduled")
                
                # Add notes for open days (with reasons)
                for note in day_schedule.get("notes", []):
                    if note:
                        output_lines.append(f"  NOTE: {note}")
    
    # Regular weekly schedule
    if schedule_data.get("future_regular_schedule"):
        output_lines.append("\n\n=== REGULAR HOURS (Standard Weekly Schedule) ===")
        for day, events in schedule_data["future_regular_schedule"].items():
            output_lines.append(f"\n{day}:")
            for event_type, sessions in events.items():
                output_lines.append(f"  {event_type}:")
                for session in sessions:
                    output_lines.append(f"    {session['time']} - {session['ages']}")
    
    return "\n".join(output_lines)

async def download_google_sheet(sheet_id: str, output_dir="downloads") -> str:
    """Download full Google Sheet as XLSX and save with timestamp (ms)."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp_ms = int(time.time() * 1000)
    file_path = os.path.join(output_dir, f"{uuid.uuid4().hex}.xlsx")

    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to download sheet (HTTP {resp.status})")
            content = await resp.read()
            with open(file_path, "wb") as f:
                f.write(content)

    # print(f"✅ Downloaded: {file_path}")
    return file_path
async def process_promotions(df_promotion):
    california_tz = await get_california_time(timezone)
    current_date = california_tz.strftime("%m-%d-%Y")
    df_promotion['Date'] = pd.to_datetime(df_promotion['Date'], format="%m-%d-%Y")
    # df_promotion = df_promotion[df_promotion['Date'] >= current_date]
    df_promotion = df_promotion.loc[df_promotion['Date'] >= current_date].copy()
    df_promotion['Date'] = df_promotion['Date'].dt.strftime("%m-%d-%Y")
    
    promotions_dict = {}
    for _, row in df_promotion.iterrows():
        codes = row["Promotion Code"].split(";")
        details = row["Details"].split(";")
        applicable_with = row['applicable_with'].split(";")
        key = row["Date"]
        for i in range(len(codes)):
            promotions_dict.setdefault(key, []).append(
                (codes[i].strip(), details[i].strip(), applicable_with[i].strip(), row['Day'])
            )


    # print(promotions_dict)
    return promotions_dict

async def format_promotions_dict(promotions_dict):
    by_code, by_category, by_date = {}, {}, {}

    def format_date(date_val):
        if isinstance(date_val, pd.Timestamp):
            dt = date_val.to_pydatetime()
        elif isinstance(date_val, str):
            dt = datetime.strptime(date_val, "%m-%d-%Y")
        else:
            raise ValueError(f"Unsupported type: {type(date_val)}")
        return dt.strftime("%B %d, %Y")

    # Build dictionaries
    for date, promos in promotions_dict.items():
        formatted_date = format_date(date)
        for code, detail, category, day in promos:
            code = code if is_valid(code) else ""
            category = category if is_valid(category) else ""

            # --- By Code ---
            if code:
                if code not in by_code:
                    by_code[code] = {
                        "details": detail,
                        "category": category,
                        "dates": []
                    }
                by_code[code]["dates"].append(f"{formatted_date} ({day})")

            # --- By Category ---
            if category:
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append((formatted_date, day, code, detail))

            # --- By Date ---
            if formatted_date not in by_date:
                by_date[formatted_date] = []
            by_date[formatted_date].append((code, detail, category, day))

    result = ""

    # ==========================================================
    # 1) BY CODE  (Write only if we actually have items)
    # ==========================================================
    if by_code:
        result += "=== promotion data filtered with promotion code ===\n"
        for code, info in by_code.items():
            result += f"{code};\n"
            result += f"     this promotional code offer is available on Dates: {', '.join(info['dates'])}\n"
            result += f"     using this promotional offer you will get: {info['details']}\n"
            result += f"     you can avail this promotional offer if you purchase {info['category']}\n\n"
        result += "=== end of promotion data filtered with promotion code ===\n\n"

    # ==========================================================
    # 2) BY CATEGORY  (Write only if we actually have items)
    # ==========================================================
    if by_category:
        result += "=== By Category ===\n"
        for cat, entries in by_category.items():
            result += f"to avail promotions that are scheduled with {cat}\n"
            for formatted_date, day, code, detail in entries:
                if code:
                    result += (
                        f"use promotional code: {code} | and you will get: {detail} "
                        f"| is offered on {formatted_date} ({day})\n"
                    )
                else:
                    result += (
                        f"Promotion is offered on {formatted_date} ({day}) "
                        f"and you will get: {detail}\n"
                    )
            result += "\n"
        result += "=== end of promotion data filtered with the category ===\n\n"

    # ==========================================================
    # 3) BY DATE  (Write only if we actually have items)
    # ==========================================================
    if by_date:
        result += "=== By Date and Day ===\n"
        for formatted_date, entries in by_date.items():
            result += f"{formatted_date};\n"
            for code, detail, category, day in entries:
                if code and category:
                    result += (
                        f"to avail this promotion use promotion code: {code} "
                        f"| and you will get: {detail} | they are offered with {category} purchase."
                        f"This promotion is only offered on {formatted_date} ({day})\n"
                    )
                elif code:
                    result += (
                        f"to avail this promotion use promotion code: {code} "
                        f"| and you will get: {detail}. This promotion is only offered on "
                        f"{formatted_date} ({day})\n"
                    )
                elif category:
                    result += (
                        f"Promotion is offered on {formatted_date} ({day}) and you will get: "
                        f"{detail} | they are offered with {category} purchase\n"
                    )
                else:
                    result += (
                        f"Promotion is offered on {formatted_date} ({day}) and you will get: "
                        f"{detail}\n"
                    )
            result += "\n"
        result += "=== end of promotion data filtered with promotion date and day ===\n\n"

    # Add footer only if ANY section has data
    if by_code or by_category or by_date:
        result += "##these promotions are available for in app purchase only. if you want then i can share our app link with you via SMS##"
        result = f"""
            ## Start of  Promotion Flow ##
                Respond with promotion info only when the user's message includes:

                    - A promotion code

                    - Mentions of promotions/deals

                    - Jump_pass or membership promotions

                    - Date-specific promotion inquiries

                    - offers

                    - Discount codes

                When a valid promo inquiry is detected:

                1.Promotion Benefits

                    Start with: "With [promotion/offer], you'll get:"

                    List key benefits.

                    In-App Purchase Disclaimer

                2.Always include one of these clearly:

                    "Important: This promotion is valid only for in-app purchases."

                    "Please note: This offer can only be redeemed through the mobile app."

                    Additional Rules:

                    Always show the first 2 to 3 promotions and ask if the user wants more.

                ### Promotional Data ###
                {result}
        """
        

    return result


async def clean_text_reverse(text):
    # 1. lower all words
    text = text.lower()
    # 2. remove everything in brackets (before removing special chars)
    text = re.sub(r'\(.*?\)', '', text)
    # 3. remove special characters (except spaces)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # 4. remove extra spaces (leading/trailing and multiple spaces)
    text = re.sub(r'\s+', ' ', text).strip()
    # 5. remove word "pitcher of"
    text = text.replace("pitcher of", "")
    # clean again for extra spaces after removal
    text = re.sub(r'\s+', ' ', text).strip()
    return text


async def clean_cost(value: str) -> float:
    value = str(value)
    numeric = re.sub(r"[^0-9.]", "", value)   # remove everything except digits and dot
    return float(numeric) if numeric else 0.0
async def format_existing_booking_details(booking,is_edit_details,reverse_mapping_roller_products):
    existing_booking_details = {

    }
    if is_edit_details:
        session_time = ""
        party_package = None
        # package_additional_jumper = None
        package_additional_jumper_quantity = 0
        food_included_selected = ""
        drink_included_selected = ""




        addons = {

        }
        ## extracting comments
        booking_notes = booking.get("bookingNotes",None)
        if booking_notes:
            booking_notes = booking_notes.lower()
            if "food selected" in booking_notes:
                food_included_selected = booking_notes.split("food selected:")[1].split("drinks selected:")[0].strip()
            if "drinks selected" in booking_notes:
                drink_included_selected = booking_notes.split("drinks selected:")[1].strip()

        # --- Process booking items ---
        for item in booking.get("items", []):
            # p_type = item.get("type")
            # product_name = item.get("productName", "")
            product_id = int(item.get("productId"))
            product_cost = item.get("cost")
            quantity = item.get("quantity", 0)
            # p_type = reverse_mapping_roller_products[product_id]["type"]
            product_details = reverse_mapping_roller_products.get(product_id, None)
            if product_details:
                product_type = product_details["type"]
                ### birthday party package
                if product_type=="birthday_party_package":
                    session_time = item.get("sessionStart",None)
                    party_package = product_details["package_name"]

                ##additional jumpers
                if product_type=="additional_jumper":
                    package_additional_jumper_quantity = item.get("quantity",0)

                ## additional food,drinks addons
                if product_type=="food_drinks_addon":
                    product_name = product_details.get("product_name",None)
                    quantity = item.get("quantity",0)
                    cost = item.get("cost",0)
                    sub_type = product_details.get("sub_type",None)
                    if sub_type not in addons:
                        addons[sub_type] = {}
                        addons[sub_type][product_name] = {
                            "quantity": quantity,
                            "cost": cost
                        }


        
        
        existing_booking_details = {
                "booking_id": booking.get("booking_id", None),
                "food_included_selected": food_included_selected,
                "drink_included_selected": drink_included_selected,
                "first_name": booking.get("first_name", None),
                "last_name": booking.get("last_name", None),
                "phone_number": booking.get("phone", None),
                "booking_status": booking.get("bookingStatus", None),
                "booking_date": booking.get("bookingDate", None),
                "email": booking.get("email", None),
                "session_time": session_time,
                "party_package": party_package,
                "package_additional_jumper_quantity": package_additional_jumper_quantity,
                "addons": addons,
                "total_cost": booking.get("total_cost", 0.0)
            }
    else:
        return existing_booking_details

async def food_drinks_prompt(df_food_drinks,is_booking_bot,df_inclusions_addons_categories,inclusions_addons_mapping,reverse_mapping_roller_products,is_edit_bot,is_edit_details,edit_booking_details_tuple):
    max_step_counter_edit = 0
    food_drinks_addons_options_dict_for_prompt = {

    }
    df_inclusions_addons_categories_edit = pd.DataFrame()
    if is_edit_bot=="yes":
        df_inclusions_addons_categories_edit = df_inclusions_addons_categories.copy()
    
    if is_booking_bot=="yes":
        df_inclusions_addons_categories["category"] = df_inclusions_addons_categories["category"].astype("str").str.lower().str.strip()
        df_inclusions_addons_categories = df_inclusions_addons_categories[df_inclusions_addons_categories["prompt_type"]=="direct_booking"]
        df_inclusions_addons_categories["step_counter"] = pd.to_numeric(df_inclusions_addons_categories["step_counter"], errors="coerce").astype("Int64")
        df_inclusions_addons_categories = df_inclusions_addons_categories.sort_values(by="step_counter", ascending=True)
        max_step_counter = df_inclusions_addons_categories.loc[df_inclusions_addons_categories["step_counter"] < 999, "step_counter"].max()
        df_food_drinks["Category"] = df_food_drinks["Category"].str.lower().str.strip()
    if is_edit_bot=="yes":
        
        df_inclusions_addons_categories_edit["category"] = df_inclusions_addons_categories_edit["category"].astype("str").str.lower().str.strip()
        df_inclusions_addons_categories_edit = df_inclusions_addons_categories_edit[
            (df_inclusions_addons_categories_edit["prompt_type"] != "direct_booking") &
            (df_inclusions_addons_categories_edit["prompt_type"].notna())
            ]
        df_inclusions_addons_categories_edit["step_counter"] = pd.to_numeric(df_inclusions_addons_categories_edit["step_counter"], errors="coerce").astype("Int64")
        df_inclusions_addons_categories_edit = df_inclusions_addons_categories_edit.sort_values(by="step_counter", ascending=True)
        max_step_counter_edit = df_inclusions_addons_categories_edit.loc[df_inclusions_addons_categories_edit["step_counter"] < 999, "step_counter"].max()
        df_food_drinks["Category"] = df_food_drinks["Category"].str.lower().str.strip()

    
    # print(df_inclusions_addons_categories)
    ##### food and drinks options

    df_food_drinks["Price"].astype(str).str.replace(".", " point ", regex=False)
    

    df_food_drinks["category_priority"] = pd.to_numeric(df_food_drinks["category_priority"], errors="coerce").astype("Int64")
    df_food_drinks = df_food_drinks.sort_values(by="category_priority", ascending=True)

    # Initialize prompt text
    final_food_drinks_prompt = ""
    final_booking_food_drinks_prompt = ""

    # Iterate through priorities
    for priority in sorted(df_food_drinks["category_priority"].dropna().unique()):
        df_priority = df_food_drinks[df_food_drinks["category_priority"] == priority]
        
        # Process by category
        for category in df_priority["Category"].unique():
            df_category = df_priority[df_priority["Category"] == category]
            category_name_for_inclusions_addons_mapping = ""
            category_name_for_reverse_mapping = ""
            

            # Add category title
            if category=="others_donot_include_just_tell_upon_mentioning":
                category_name_for_inclusions_addons_mapping = "addons"
                category_name_for_reverse_mapping = "addons"
                category_title = f"\n**Other Party Addon options (Donot Tell Until user mentions):**\n"
                category_title_unchanged = "Other Party Addon options (Donot Tell Until user mentions)"
            else:
                category_name_for_inclusions_addons_mapping = str(category).lower().replace("_", " ")
                category_name_for_reverse_mapping = str(category).lower()
                if (df_category["category_type"] == "included_in_package").any():
                    category_title = f"\n **{category.replace('_',' ' ).capitalize()}(Included In Birthday Party Package) options:**\n"
                    category_title_unchanged = category.replace("_"," ").capitalize()
                else:
                    category_title = f"\n **{category.replace('_',' ').capitalize()} options:**\n"
                    category_title_unchanged = category.replace("_"," ").capitalize()

            
            # Case 1: Included in package
            if (df_category["category_type"] == "included_in_package").any():
                # Primary options
                primary_items = df_category[df_category["options_type_per_category"] == "primary"]
                if not primary_items.empty:
                    category_title += f"Here are the popular {category_title_unchanged} options:\n"
                    for _, row in primary_items.iterrows():

                        roller_id_available = pd.notna(row["roller_product_id"]) and str(row["roller_product_id"]).lower() != "nan"
                        if is_booking_bot=="yes":
                            if roller_id_available:
                                ## adding reverse and search ids
                                item_name_temp = row['Item']
                                price_temp = row['Price']
                                booking_id = row['roller_product_id']
                                key = await clean_text_reverse(item_name_temp)
                                inclusions_addons_mapping[key] =  {
                                    "booking_id": booking_id,
                                    "cost": price_temp,
                                    "category":category_name_for_inclusions_addons_mapping
                                    
                                }

                                if booking_id not in list(reverse_mapping_roller_products.keys()):
                                    reverse_mapping_roller_products[booking_id] = {
                                        "type":"food_drinks_addon",
                                        
                                        "sub_type":category_name_for_reverse_mapping,
                                        "product_name" : key,
                                        "cost": price_temp

                                    }
                                ## end of adding reverse and search ids
                                category_title += f"- {row['Item']} ({row['additional_instructions']}) | Price($):{row['Price']} \n"
                        else:    
                            ## end of adding reverse and search ids
                            category_title += f"- {row['Item']} ({row['additional_instructions']}) | Price($):{row['Price']} \n"

                # Secondary options
                secondary_items = df_category[df_category["options_type_per_category"] == "secondary"]
                if not secondary_items.empty:
                    category_title += f"\nDo you want to know about other {category_title_unchanged} options? if user says 'yes' then tell below:\n"
                    for _, row in secondary_items.iterrows():
                        roller_id_available = pd.notna(row["roller_product_id"]) and str(row["roller_product_id"]).lower() != "nan"
                        if is_booking_bot=="yes":
                            if roller_id_available:
                                ## adding reverse and search ids
                                item_name_temp = row['Item']
                                price_temp = row['Price']
                                booking_id = row['roller_product_id']
                                key = await clean_text_reverse(item_name_temp)
                                inclusions_addons_mapping[key] =  {
                                    "booking_id": booking_id,
                                    "cost": price_temp,
                                    "category":category_name_for_inclusions_addons_mapping
                                }

                                if booking_id not in list(reverse_mapping_roller_products.keys()):
                                    reverse_mapping_roller_products[booking_id] = {
                                        "type":"food_drinks_addon",
                                        "sub_type":category_name_for_reverse_mapping,
                                        
                                        "product_name" : key,
                                        "cost": price_temp

                                    }
                                
                                ## end of adding reverse and search ids
                                category_title += f"- {row['Item']} ({row['additional_instructions']}) | Price($):{row['Price']}\n"
                        else:
                            category_title += f"- {row['Item']} ({row['additional_instructions']}) | Price($):{row['Price']}\n"

            # Case 2: Addons (priority != 999)
            elif (df_category["category_type"] == "addon").any() and priority != 999:
                category_title += " (These are available as add-ons:)"
                # Primary options
                primary_items = df_category[df_category["options_type_per_category"] == "primary"]
                if not primary_items.empty:
                    category_title += f"Here are the popular {category_title_unchanged} options:\n"
                    for _, row in primary_items.iterrows():
                        roller_id_available = pd.notna(row["roller_product_id"]) and str(row["roller_product_id"]).lower() != "nan"
                        if is_booking_bot=="yes":
                            if roller_id_available:
                                ## adding reverse and search ids
                                item_name_temp = row['Item']
                                price_temp = row['Price']
                                booking_id = row['roller_product_id']
                                key = await clean_text_reverse(item_name_temp)
                                inclusions_addons_mapping[key] =  {
                                    "booking_id": booking_id,
                                    "cost": price_temp,
                                    "category":category_name_for_inclusions_addons_mapping
                                }

                                if booking_id not in list(reverse_mapping_roller_products.keys()):
                                    reverse_mapping_roller_products[booking_id] = {
                                        "type":"food_drinks_addon",
                                        "sub_type":category_name_for_reverse_mapping,
                                        "product_name" : key,
                                        "cost": price_temp

                                    }
                                
                                ## end of adding reverse and search ids
                                category_title += f"- {row['Item']} ({row['additional_instructions']}) | Price($):{row['Price']} \n"
                        else:
                            category_title += f"- {row['Item']} ({row['additional_instructions']}) | Price($):{row['Price']} \n"
                # Secondary options
                secondary_items = df_category[df_category["options_type_per_category"] == "secondary"]
                if not secondary_items.empty:
                    category_title += f"\nDo you want to know about other {category_title_unchanged} options? if user says 'yes' then tell below:\n"
                    for _, row in secondary_items.iterrows():
                        roller_id_available = pd.notna(row["roller_product_id"]) and str(row["roller_product_id"]).lower() != "nan"
                        if is_booking_bot=="yes":
                            if roller_id_available:
                                ## adding reverse and search ids
                                item_name_temp = row['Item']
                                price_temp = row['Price']
                                booking_id = row['roller_product_id']
                                key = await clean_text_reverse(item_name_temp)
                                inclusions_addons_mapping[key] =  {
                                    "booking_id": booking_id,
                                    "cost": price_temp,
                                    "category":category_name_for_inclusions_addons_mapping
                                }

                                if booking_id not in list(reverse_mapping_roller_products.keys()):
                                    reverse_mapping_roller_products[booking_id] = {
                                        "type":"food_drinks_addon",
                                        "sub_type":category_name_for_reverse_mapping,
                                        "product_name" : key,
                                        "cost": price_temp

                                    }
                                
                                ## end of adding reverse and search ids
                                if row['additional_instructions']=="nan" or pd.isna(row['additional_instructions']):
                                    recommendations = ""
                                else:
                                    recommendations  = f"({row['additional_instructions']})"
                                    
                                category_title += f"- {row['Item']} {recommendations} | Price($):{row['Price']}\n"
                        else:
                            category_title += f"- {row['Item']} ({row['additional_instructions']}) | Price($):{row['Price']}\n"
            # Case 3: Addons (priority == 999)
            elif (df_category["category_type"] == "addon").any() and priority == 999:
                category_title += "These add-ons are available (only mention if user explicitly asks):\n"
                for _, row in df_category.iterrows():
                    roller_id_available = pd.notna(row["roller_product_id"]) and str(row["roller_product_id"]).lower() != "nan"
                    if is_booking_bot=="yes":
                        if roller_id_available:
                            ## adding reverse and search ids
                            item_name_temp = row['Item']
                            price_temp = row['Price']
                            booking_id = row['roller_product_id']
                            key = await clean_text_reverse(item_name_temp)
                            inclusions_addons_mapping[key] =  {
                                "booking_id": booking_id,
                                "cost": price_temp,
                                "category":category_name_for_inclusions_addons_mapping
                            }

                            if booking_id not in list(reverse_mapping_roller_products.keys()):
                                reverse_mapping_roller_products[booking_id] = {
                                    "type":"food_drinks_addon",
                                    "sub_type":category_name_for_reverse_mapping,
                                    "product_name" : key,
                                    "cost": price_temp

                                }
                            
                            ## end of adding reverse and search ids
                            category_title += f"- {row['Item']} ({row['additional_instructions']}) | Price($):{row['Price']}\n"
                    else:
                        category_title += f"- {row['Item']} ({row['additional_instructions']}) | Price($):{row['Price']}\n"
            food_drinks_addons_options_dict_for_prompt[category] = category_title
            final_food_drinks_prompt += category_title
    existing_booking_details = {}
    edit_food_prompt = """"""
    
    if is_edit_bot == "yes":
        existing_booking_details = await format_existing_booking_details(edit_booking_details_tuple,is_edit_details,reverse_mapping_roller_products)
   
    
    if is_edit_bot=="yes":
        for _,row in df_inclusions_addons_categories_edit.iterrows():
            food_addon_options_per_category = food_drinks_addons_options_dict_for_prompt.get(row['category'],None)
            additional_instruction = ""
            user_selections = ""
           
            if food_addon_options_per_category:
                ## food inclusion and food addons
                if row["prompt_type"]=="edit_inclusion_food":
                    if existing_booking_details.get("food_included_selected",None):
                        additional_instruction = f"User have selected {row['category']  } inclusions available in {existing_booking_details['party_package']} : {existing_booking_details.get('food_included_selected')}"
                        user_selections = existing_booking_details.get('food_included_selected')

                    else:
                        if "basic" not in existing_booking_details["party_package"]:
                            additional_instruction = f"User has not selected 2 {row['category']} Included in {existing_booking_details['party_package']} Please ask user to select two {row['category']} flavours"

                    existing_booking_addons_food = existing_booking_details.get("addons",None)
                    if existing_booking_addons_food:

                        existing_booking_addons_food = existing_booking_addons_food.get(row['category'],None)
                        if existing_booking_addons_food:
                            user_addon_selections = await format_addons_for_edit(existing_booking_addons_food)
                            additional_instructions += f"\n User has selected these {row['category']  } addons: {user_addon_selections}"
                            if user_selections=="":
                                user_selections = user_selections
                            else:
                                user_selections = user_selections + ","+user_addon_selections

                ###Drinks inclusions and addons
                elif row["prompt_type"]=="edit_inclusion_drinks":
                    if existing_booking_details.get("drink_included_selected",None):
                        additional_instruction = f"User have selected {row['category']  } inclusions available in {existing_booking_details['party_package']} : {existing_booking_details.get('drink_included_selected')}"
                        user_selections = existing_booking_details.get('drink_included_selected')

                    else:
                        if "basic" not in existing_booking_details["party_package"]:
                            additional_instruction = f"User has not selected 2 {row['category']} Included in {existing_booking_details['party_package']} Please ask user to select two {row['category']} flavours"

                    existing_booking_addons_food = existing_booking_details.get("addons",None)
                    if existing_booking_addons_food:

                        existing_booking_addons_food = existing_booking_addons_food.get(row['category'],None)
                        if existing_booking_addons_food:
                            user_addon_selections = await format_addons_for_edit(existing_booking_addons_food)
                            additional_instructions += f"\n User has selected these {row['category']  } addons: {user_addon_selections}"
                            if user_selections=="":
                                user_selections = user_selections
                            else:
                                user_selections = user_selections + ","+user_addon_selections

                #### Party Trays and addons:
                 ###Drinks inclusions and addons
                else:
                    
                    existing_booking_addons_food = existing_booking_details.get("addons",None)
                    if existing_booking_addons_food:

                        existing_booking_addons_food = existing_booking_addons_food.get(row['category'],None)
                        if existing_booking_addons_food:
                            user_addon_selections = await format_addons_for_edit(existing_booking_addons_food)
                            additional_instructions = ""
                            if user_selections=="":
                                user_selections = user_selections
                            else:
                                user_selections = user_selections + ","+user_addon_selections


                
                edit_food_prompt += f""" \n
                {row['prompt_start'].replace("user_selected_options",user_selections).replace("additional_instruction",additional_instruction)} \n
                {food_addon_options_per_category} \n
                {row['prompt_end'].replace("user_selected_options",user_selections)} \n    
                 """

    if is_booking_bot=="yes":
        for _,row in df_inclusions_addons_categories.iterrows():
            food_addon_options_per_category = food_drinks_addons_options_dict_for_prompt.get(row['category'],None)
            if food_addon_options_per_category:
                final_booking_food_drinks_prompt += f""" \n
                {row['prompt_start']} \n
                {food_addon_options_per_category} \n
                {row['prompt_end']} \n


                 """
        return final_booking_food_drinks_prompt,inclusions_addons_mapping,reverse_mapping_roller_products,max_step_counter,edit_food_prompt,existing_booking_details,max_step_counter_edit 
        
        
    else:
        return final_food_drinks_prompt,inclusions_addons_mapping,reverse_mapping_roller_products,0,edit_food_prompt,existing_booking_details,max_step_counter_edit
    
async def format_addons_for_edit(addon_dict):
    addon_selection = ""
    for key in list(addon_dict.keys()):
        addon_detail = addon_dict["key"]
        for i in range(0,int(addon_detail["quantity"])):
            if addon_selection:
                addon_selection = key
            else:
                addon_selection = addon_selection +","+key

    return addon_selection


async def reassign_pitch_priority(df):
    # Step 1: Split into two groups
    
    df_fixed = df[df["pitch_priority"] == 999].copy()
    df_reassign = df[df["pitch_priority"] != 999].copy()

    # Step 2: Sort df_reassign by original priority (to preserve order)
    df_reassign = df_reassign.sort_values(by="pitch_priority")

    # Step 3: Assign new sequential priorities starting from 1
    df_reassign["pitch_priority"] = range(1, len(df_reassign) + 1)

    # Step 4: Combine back
    df_final = pd.concat([df_fixed, df_reassign], ignore_index=True)

    # Step 5: Optional — sort back by pitch_priority for readability
    df_final = df_final.sort_values(by="pitch_priority")

    return df_final
async def process_birthday_food(df_party_packages,df_food_drinks,hours_df,guest_of_honor_included_in_minimum_jumpers_party,minimum_jumpers_party,add_additional_hour_of_jump_instruction,add_additional_half_hour_of_jump_instruction,is_booking_bot,df_inclusions_addons_categories,is_edit_bot,is_edit_details,edit_booking_details_tuple,pitch_ballons_while_booking,additional_jumper_discount,roller_product_ids):

    clean_text = lambda s: " ".join(
    re.sub(r"[^a-z0-9\s]", "",                 # remove special chars
    re.sub(r"\(.*?\)", "",                     # remove (...) including content
    s.lower().replace("pitcher of", "")))      # remove "pitcher of"
    .split()
    )
    birthday_mappings = {}
    # pizzas_mapping = {}
    # drinks_mapping = {}
    inclusions_addons_mapping = {}

    # reverse mapping
    reverse_mapping_roller_products= {}
    
    if is_booking_bot=="yes":
        condition = (df_party_packages["roller_birthday_party_search_id"] != "nan") & \
            (pd.notna(df_party_packages["roller_birthday_party_search_id"]))
        

        df_party_packages = df_party_packages[condition]
        if not df_party_packages.empty:
            df_party_packages["roller_birthday_party_search_id"] = (pd.to_numeric(df_party_packages["roller_birthday_party_search_id"],
                                                                     errors="coerce")
                                                                    .astype("Int64")
                                                                    )
            df_party_packages["pitch_priority"] = (pd.to_numeric(df_party_packages["pitch_priority"],
                                        errors="coerce")
                                        .astype("Int64")
                                        )
            
            df_party_packages["roller_birthday_party_booking_id"] = (pd.to_numeric(df_party_packages["roller_birthday_party_booking_id"],
                                                                     errors="coerce")
                                                                    .astype("Int64")
                                                                    )
            df_party_packages["roller_additional_jumper_id"] = (pd.to_numeric(df_party_packages["roller_additional_jumper_id"],
                                                                     errors="coerce")
                                                                    .astype("Int64")
                                                                    )
            df_party_packages["roller_additional_jump_hour_id"] = (pd.to_numeric(df_party_packages["roller_additional_jump_hour_id"],
                                                                     errors="coerce")
                                                                    .astype("Int64")
                                                                    )
            
            df_food_drinks["roller_product_id"] = (pd.to_numeric(df_food_drinks["roller_product_id"],
                                                                     errors="coerce")
                                                                    .astype("Int64")
                                                                    )
            ### Applying filtering so that if roller product is not present booking bot should not present it

            roller_product_ids = pd.to_numeric(roller_product_ids, errors="coerce")
            roller_product_ids = pd.Series(roller_product_ids).dropna().astype("Int64")

            df_party_packages = df_party_packages[
                df_party_packages["roller_birthday_party_search_id"].isin(roller_product_ids)
                & df_party_packages["roller_birthday_party_booking_id"].isin(roller_product_ids)
                & df_party_packages["roller_additional_jumper_id"].isin(roller_product_ids)
            ]
            # print(roller_product_ids)
            df_food_drinks = df_food_drinks[df_food_drinks["roller_product_id"].isin(roller_product_ids)]
            # print(df_food_drinks)
            ### reassigning priority if priority 1 product is not present in roller ids
            if df_party_packages[df_party_packages["pitch_priority"]!=1].empty: 
                df_party_packages = await reassign_pitch_priority(df_party_packages)


    birthday_party_packages = ""
    birthday_party_prompt = ""
    most_popular_package_name = ""
    most_popular_birthday_package_prompt = ""
    most_popular_birthday_package_prompt_for_edit = ""

    hours_jump_type_unique_values = hours_df['jump_type'].unique().tolist() 
    other_birthday_packages_prompt = "### Other Birthday Party Packages options"
    other_birthday_packages_prompt += "\n Please construct Natural Sentences and only List Down Other Pacakages Names"
    other_birthday_packages_available_always = ""
    other_birthday_packages_available_certain_days = ""
    other_birthday_packages_donot_mention_until_asked = ""
    ## case birthday package is not available for schedule with but jump pass is  available
    birthday_packages_available_for_celebrating = []
    # print(df_party_packages["schedule_with"].unique())
    for sched in list(df_party_packages["schedule_with"].unique()):
        packages_filtered_with_schedule = df_party_packages[df_party_packages["schedule_with"]==sched]
        

        schedule_with_list = sched.split(",")
        cleaned_schedule_with_list = []
        for single_schedule_with in schedule_with_list:
            clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', single_schedule_with).strip()
            clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
            section_title = clean_sched_name.replace(' ', ' ').title()
            section_title = section_title + "Hours (Session)"
            cleaned_schedule_with_list.append(section_title)

            if single_schedule_with not in birthday_packages_available_for_celebrating:
                birthday_packages_available_for_celebrating.append(single_schedule_with)
        scheduling_instruction = ""
        if len(schedule_with_list)>1:
            section_title = " and ".join(cleaned_schedule_with_list) 
            # extra_instruction = f"(The below jump pass or jump tickets are available during {len(schedule_with_list)} sessions ( {sched}) hours)"
            scheduling_instruction = f" - Schedule Below Birthday party packages with {len(schedule_with_list)} sessions {section_title} available in hours of operation for requested date or day - only tell  user below Birthday Party Packages if available for requested date or day: \n"
        else:
            section_title = "".join(cleaned_schedule_with_list)
            scheduling_instruction = f"\n - Schedule Below Birthday party packages with {sched.replace('_',' ' )} available in hours of operation for requested date or day - only tell  user below Birthday Party Packages if available for requested date or day: \n" 
        
        birthday_party_packages += f"### {section_title} Birthday Party Packages \n"
        birthday_party_packages += scheduling_instruction
        birthday_party_packages += f"\n Birthday Party Pacakges that schedule with {section_title} : \n"
        
        
        
        for _, row in packages_filtered_with_schedule.iterrows():

            package_name = row['package_name']
            other_perks = row['other_perks']
            key = clean_text(package_name)
            price = row['Price']
            package_celebration_environment = (str(row.get("party_environment_name","party room")).title()) + " Time"
            package_price_for_dict = await clean_cost(row['Price'])
            food_included_count = int(row["food_included_count"])
            drinks_included_count = int(row["drinks_included_count"])
            roller_birthday_party_search_id = row['roller_birthday_party_search_id']
            roller_birthday_party_booking_id = row['roller_birthday_party_booking_id']
            roller_additional_jumper_search_id = row['roller_additional_jumper_id']
            additional_jumper_price = await clean_cost(row['additional_jumper_price'])
            package_minimum_jumpers =  row['minimum_jumpers']
            package_jump_time  =  row['jump_time']
            package_party_room_time  =  row['party_room_time']
            package_food_and_drinks =  row['Food_and_drinks']
            package_paper_goods  =  row['paper_goods']
            package_sky_socks  =  row['Skysocks']
            package_dessert  =  row['Dessert']
            package_price_multiply_with_number_of_jumpers = (row.get("multiply","no"))=="yes"
            
            package_guest_of_honor_shirt_included  =  row['Guest of honor']
            include_t_shirt = False
            if is_valid(package_guest_of_honor_shirt_included):
                include_t_shirt = "no" not in ((package_guest_of_honor_shirt_included.lower()).split(" "))
            package_outside_food_drinks_policy  =  row['outside_food_drinks']
            if row["tax_included_package_price"] == "no":

                package_price  = "$ "+ str(row['Price']).strip().replace("."," point ") + "without Tax"
            else:
                package_price  = "$ "+ str(row['Price']).strip().replace("."," point ")
            package_additional_jumper_price = "$ "+ str(row['additional_jumper_price']).strip().replace("."," point ")

            pitch_introduction = row["pitch_introduction"]
            priority = str(row["pitch_priority"]).strip().replace(" ","")

            
            availability = row["availability_days"]
            #print(priority)

            package_additional_jumper_threshold = ""
            package_additional_jumper_discounted_price = ""
            Additional_jumper_discount_sentence = ""

            if additional_jumper_discount == "yes":
                package_additional_jumper_threshold = row.get('Additional_Jumper_Discount_Threshold', "")
                package_additional_jumper_discounted_price = row.get('Discounted_Additional_Jumper_Price', "")
                if is_valid(package_additional_jumper_threshold):
                    Additional_jumper_discount_sentence = f"- If there are {package_additional_jumper_threshold} or more additional jumper the price will be {package_additional_jumper_discounted_price} dollars per jumper ."
                else:
                    Additional_jumper_discount_sentence = ""
            # print(f"{Additional_jumper_discount_sentence}")


            balloon_package_credit = ""
            ballon_package = ""
            balloon_promo_code = ""
            balloon_sentence = ""
            
            minimum_jumpers_sentence = ""
            additional_hour_sentence = ""
            additional_half_hour_sentence = ""

            if pitch_ballons_while_booking == "yes":
                balloon_package_credit = row.get('balloon_package_credit', "")
                ballon_package = row.get('balloon_package', "")
                balloon_promo_code = row.get('balloon_avail_code', "")

                if is_valid(ballon_package) and is_valid(balloon_package_credit) and is_valid(balloon_promo_code):
                    balloon_sentence = f"- Get a free {ballon_package} or use your ${balloon_package_credit} balloon credit for larger package with code {balloon_promo_code}."
                elif is_valid(ballon_package) and is_valid(balloon_package_credit):
                    balloon_sentence = f"- Get ${balloon_package_credit} off balloon packages with the {ballon_package}."
                elif is_valid(ballon_package):
                    balloon_sentence = f"- Get a free {ballon_package}."
                elif is_valid(balloon_package_credit):
                    balloon_sentence = f"- ${balloon_package_credit} credit for balloon packages only."
                else:
                    balloon_sentence = ""
            else:
                balloon_sentence = ""

            # print(f"balloon sentence: {balloon_sentence}")

            if guest_of_honor_included_in_minimum_jumpers_party=="yes":
                minimum_jumpers_sentence = f"{package_minimum_jumpers} jumpers including Guest of Honor"
            else:
                 minimum_jumpers_sentence = f"{package_minimum_jumpers} jumpers included"

            if add_additional_hour_of_jump_instruction=="yes":
                additional_hour_sentence = f"""- Additional Hour of Jump Time After Party Room / Party Space / Open Air Party Time(addon): {row['additional_jump_hour_after_room_time']}.
                 """
            if add_additional_half_hour_of_jump_instruction == "yes":
                additional_half_hour_sentence = f"""- Additional Half Hour of Jump Time After Party Room /Party Space/Open Air Party Time(addon): {row['additional_jump_half_hour_after_room_time']} .
                 """

            if is_booking_bot=="yes":
                birthday_mappings[key] = {
                    'type' : "birthday_party_package",
                    'roller_birthday_party_search_id': roller_birthday_party_search_id, 
                    'booking_package_id': roller_birthday_party_booking_id,
                    'additional_jumper_id':roller_additional_jumper_search_id,
                    'booking_package_cost': package_price_for_dict,
                    "additional_jumper_cost": additional_jumper_price,
                    "food_included_count":food_included_count,
                    "drinks_included_count":drinks_included_count,
                    "package_price_multiply_with_number_of_jumpers":package_price_multiply_with_number_of_jumpers,
                    "include_t_shirt":include_t_shirt,


                }
                 ##adding birthday party package in reverse
                reverse_mapping_roller_products[roller_birthday_party_booking_id] = {
                    'type' : "birthday_party_package",
                    "package_name" : await clean_text_reverse(package_name),
                    'roller_birthday_party_search_id': roller_birthday_party_search_id, 
                    'booking_package_id': roller_birthday_party_booking_id,
                    'additional_jumper_id':roller_additional_jumper_search_id,
                    'booking_package_cost': package_price_for_dict,
                    "additional_jumper_cost": additional_jumper_price,
                    "food_included_count":food_included_count,
                    "drinks_included_count":drinks_included_count,
                    "package_price_multiply_with_number_of_jumpers":package_price_multiply_with_number_of_jumpers,
                    "include_t_shirt":include_t_shirt,
                }
                ## adding reverse mapping of additional jumper
                reverse_mapping_roller_products[roller_additional_jumper_search_id] = {
                    "type":"additional_jumper",
                    "package_name":await clean_text_reverse(package_name),
                    "price": additional_jumper_price

                }
                if pitch_ballons_while_booking=="yes":
                    
                    birthday_mappings[key]["balloon_credit"]=await clean_cost(balloon_package_credit)
                    birthday_mappings[key]["balloon_package_included"]=ballon_package
                    birthday_mappings[key]["balloon_promo_code"]=balloon_promo_code

                    ## reverse mapping
                    reverse_mapping_roller_products[roller_birthday_party_booking_id]["balloon_credit"]=await clean_cost(balloon_package_credit)
                    reverse_mapping_roller_products[roller_birthday_party_booking_id]["balloon_package_included"]=ballon_package
                    reverse_mapping_roller_products[roller_birthday_party_booking_id]["balloon_promo_code"]=balloon_promo_code

                if additional_jumper_discount == "yes":
                    birthday_mappings[key]["additional_jumpers_discount_threshold"]=int(await clean_cost(package_additional_jumper_threshold))
                    birthday_mappings[key]["additional_jumpers_discounted_price"]= await clean_cost(package_additional_jumper_discounted_price)

                    ###reverse mapping
                    reverse_mapping_roller_products[roller_birthday_party_booking_id]["additional_jumpers_discount_threshold"]=int(await clean_cost(package_additional_jumper_threshold))

                    reverse_mapping_roller_products[roller_birthday_party_booking_id]["additional_jumpers_discounted_price"]= await clean_cost(package_additional_jumper_discounted_price)

                    

               


            if pd.isna(other_perks):
                formatted_perks = ""
            else:
                formatted_perks = ", ".join(str(other_perks).splitlines())
            
            

            ### Constructing Prompt for Most Popular Birthday Party Package and other options  
            if int(priority)==1:

                if is_booking_bot =="yes":
                    step_counter = 1
                    child_variable = "[child's name]"
                    step_one = f"""## *STEP {step_counter}.1: [Always Highlight the Most Popular Birthday {package_name}  First]*"""
                    step_two = f"""
                        ## *STEP {step_counter}.2: {package_name} Deep Dive*
                    """
                
                else:
                    step_counter = 3
                    child_variable = ""
                    step_one = f"""## *STEP {step_counter}: [Always Highlight the Most Popular Birthday {package_name}  First]*"""
                    step_two = f"""
                        ## *STEP {step_counter+1}: {package_name} Deep Dive*
                    """

                
                most_popular_package_name = package_name
                first_part = f"""

                "Perfect! Let me tell you about our most popular *{package_name}*! 
                - Construct Natural Sentences
                
                - {minimum_jumpers_sentence}
                - {package_jump_time}  
                - {package_party_room_time}
                - Includes everything to make it seamless!

                Would you like to learn more about the {package_name} or hear about other options?"


                ---
                """
                second_part = f"""
                If they want more details, present them in a conversational way

                "Here's what makes the {package_name} incredible:
                - Present the following details in more engaging and conversational way

                What's Included:
                - Minimum Jumpers: {minimum_jumpers_sentence}
                - Jump Time: {package_jump_time} 
                - {package_celebration_environment} : {package_party_room_time}
                - Food and drinks included in Package: {package_food_and_drinks}
                - Paper Goods: {package_paper_goods}. 
                - Sky Socks: {package_sky_socks}.
                - *Birthday Child T-shirt*: {package_guest_of_honor_shirt_included}.
                - Birthday Package Perks: {formatted_perks}.
                - Desserts and Cakes Policy : { package_dessert }.
                - Outside Food Fee(Policy): {package_outside_food_drinks_policy}.
                - Price (Donot mention Birthday Party Package Price until user explicitly ask for it) : {package_price}.
                - Additional Jumper Cost: {package_additional_jumper_price}.
                {additional_hour_sentence}
                {additional_half_hour_sentence}
                {balloon_sentence}
                {Additional_jumper_discount_sentence}
                

                *After explaining the {package_name} details, ask:*
                "Would you like to book this {package_name} for your {child_variable} celebration?"""

                most_popular_birthday_package_prompt = f"""
                {step_one}
                {first_part}
                {step_two}
                {second_part}
                """
                most_popular_birthday_package_prompt_for_edit = """"""
                if is_edit_bot =="yes":
                    step_counter = 2
                    child_variable = "[child's name]"
                    step_one = f"""## *STEP {step_counter}: [Always Highlight the Most Popular Birthday {package_name}  First]*"""
                    step_two = f"""
                        ## *STEP {step_counter+1}: {package_name} Deep Dive*
                    """
                    most_popular_birthday_package_prompt_for_edit = f"""
                            {step_one}
                            {first_part}
                            {step_two}
                            {second_part}
                            """

            elif int(priority)==999:
                pass

                
            else:
                if availability == "always":
                    other_birthday_packages_available_always += f"""\n - *{package_name}* {pitch_introduction} """
                    
                else:
                    other_birthday_packages_available_certain_days += f"""\n - *{package_name}[( {package_name} is available certain days Only mention if {package_name} is available on the calculated day based on schedule:]* {pitch_introduction} """
                
            
            ### end of Constructing Prompt for Most Popular Birthday Party Package and other options
            if int(priority)!=1:
                birthday_party_packages += f""" \n 
                ** {package_name} **
                - Construct Natural Sentences
                - Minimum Jumpers: {minimum_jumpers_sentence}.
                - Jump Time: {package_jump_time}.
                - {package_celebration_environment}: {package_party_room_time}.
                - Food and drinks included in Package: {package_food_and_drinks}.
                - Paper Goods: {package_paper_goods}.
                - Skysocks: {package_sky_socks}.
                -  Desserts and Cakes Policy : { package_dessert }.
                - *Birthday Child T-shirt*: {package_guest_of_honor_shirt_included}.
                - Outside Food Fee(Policy): {package_outside_food_drinks_policy}.
                - Birthday Package Perks: {formatted_perks}.
                - Price (Donot mention Birthday Party Package Price until user explicitly ask for it) : {package_price}.
                - Additional Jumper Cost: {package_additional_jumper_price}.
                {additional_hour_sentence}
                {additional_half_hour_sentence}
                {balloon_sentence}
                {Additional_jumper_discount_sentence}.
                    """

        
   
    final_food_drinks_prompt,inclusions_addons_mapping,reverse_mapping_roller_products,max_step_counter,edit_food_prompt,existing_booking_details,max_step_counter_edit = await food_drinks_prompt(df_food_drinks,is_booking_bot,df_inclusions_addons_categories,inclusions_addons_mapping,reverse_mapping_roller_products,is_edit_bot,is_edit_details,edit_booking_details_tuple)

    

    ###end of birthday packages
    if is_booking_bot=="yes":
        skyzone_food_drinks_dict ={
            "food_drinks_prompt":f"""
                                {final_food_drinks_prompt}
                                
                                """,
            "inclusions_addons_mapping":inclusions_addons_mapping,
            "reverse_mapping_roller_products":reverse_mapping_roller_products,
            "max_step_counter":max_step_counter,
            "edit_food_prompt":edit_food_prompt,
            "existing_booking_details":existing_booking_details,
            "max_step_counter_edit":max_step_counter_edit
           


        } 


    else:
        skyzone_food_drinks_dict ={
            "food_drinks_prompt":f"""
                                ####### Food and Drinks Options

                                {final_food_drinks_prompt}
                                
                                """,
            "inclusions_addons_mapping":inclusions_addons_mapping,
            "reverse_mapping_roller_products":reverse_mapping_roller_products,
            "edit_food_prompt":"",
            "existing_booking_details":{},
            "max_step_counter_edit":max_step_counter_edit


        } 

    ### Jump passes which are not present in hours of operation
    sessions_not_available_for_birthdays  = list(set(hours_jump_type_unique_values)- set(birthday_packages_available_for_celebrating) )
    
    ## case birthday package is available for jump type but jump pass is not available
    if len(sessions_not_available_for_birthdays) >0:
        for not_available_jump_session in sessions_not_available_for_birthdays:
            
            clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', not_available_jump_session).strip()
            clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
            section_title = clean_sched_name.replace(' ', ' ').title()
           
            birthday_party_packages += f""" \n ### {section_title} Birthday Party Package is not offered (Only Mention if user explicitly asks for it)"""

    birthday_party_prompt = f""" 
                ### Bithday Party Packages Data:
                {birthday_party_packages}
        """
    other_birthday_packages_prompt += "\n" + f"Donot Mention or mention {most_popular_package_name} if already explained"
    other_birthday_packages_prompt += "\n" + other_birthday_packages_available_always
    other_birthday_packages_prompt += "\n" + other_birthday_packages_available_certain_days
    other_birthday_packages_prompt += "\n" + other_birthday_packages_donot_mention_until_asked
    
    ### end of jump passes which are not present in hours of operation
    
    other_options = f"""
                    {other_birthday_packages_prompt}

    Which package would you like to hear more details about?"
"""
    birthday_party_prompt = {
        "birthday_packages_data": birthday_party_prompt,
        "most_popular_birthday_package_prompt": most_popular_birthday_package_prompt,
        "most_popular_birthday_package_prompt_for_edit":most_popular_birthday_package_prompt_for_edit,
        "other_birthday_packages_prompt" :  other_options,
        "birthday_mappings":birthday_mappings,
    }
    # print(birthday_party_prompt)
    
    return birthday_party_prompt , skyzone_food_drinks_dict


async def jump_pass_info(df: pd.DataFrame, schedule_with_dict: dict,hours_df:pd.DataFrame) -> str:
    summary = []
    
    # Get unique schedule_with values
    schedule_with_values = df['schedule_with'].unique()
    hours_jump_type_unique_values = hours_df['jump_type'].unique().tolist() 
    most_popular_pass_prompt = ""
    other_jump_passes_prompt = "### Other Jump pass options"
    other_jump_passes_prompt += "\n Please construct Natural Sentences and only List Passes Names"
    other_jump_passes_available_always = ""
    other_jump_passes_available_certain_days = ""
    other_jump_passes_donot_mention_until_asked = ""



    ## case birthday package is available for jump type but jump pass is not available
    jump_passes_available_for_jumping = []
    for sched in schedule_with_values:
        df_sched = df[df['schedule_with'] == sched]
        
        # Create clean section header
        schedule_with_list = sched.split(",")
        cleaned_schedule_with_list = []
        for single_schedule_with in schedule_with_list:
            clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', single_schedule_with).strip()
            clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
            section_title = clean_sched_name.replace(' ', ' ').title()
            section_title = section_title + "Hours (Session)"
            cleaned_schedule_with_list.append(section_title)

            if single_schedule_with not in jump_passes_available_for_jumping:
                jump_passes_available_for_jumping.append(single_schedule_with)
        scheduling_instruction = ""
        if len(schedule_with_list)>1:
            section_title = " and ".join(cleaned_schedule_with_list) 
            # extra_instruction = f"(The below jump pass or jump tickets are available during {len(schedule_with_list)} sessions ( {sched}) hours)"
            scheduling_instruction = f"Schedule Below Jump passes or Jump tickets with {len(schedule_with_list)} sessions {section_title} available in hours of operation for requested date or day - only tell user this pass if available for requested date or day"

        else:
            section_title = "".join(cleaned_schedule_with_list)
            scheduling_instruction = f"Schedule Below Jump passes or Jump tickets with {sched.replace('_',' ')} available in hours of operation for requested date or day - only tell user this pass if available for requested date or day" 

        summary.append(f"#### {section_title} Jump Passes")
        summary.append(scheduling_instruction)
        summary.append(f"Passes information that schedule with {section_title}:")
        
        summary.append("")
        
        # Group passes by type for better organization
        pass_details = []
        for _, row in df_sched.iterrows():
            pass_name = row['pass_name']
            pass_name_temp = pass_name
            temp_recommendations = row["recommendations"]
            recommendations = ""
            if temp_recommendations.strip() and temp_recommendations.replace(" ",""):
                if pd.notna(temp_recommendations) and str(temp_recommendations)!="nan":
                    recommendations = f"({temp_recommendations})"
                
            starting_day = row["starting_day_name"]
            ending_day = row["ending_day_name"]
            
            starting_day_and_ending_day = ""
            if starting_day and ending_day:
                if starting_day.replace(" ","") and ending_day.replace(" ",""):
                    if (pd.notna(starting_day) and  str(starting_day).lower() != "nan") and  (pd.notna(ending_day) and str(starting_day).lower() != "nan"):
                        starting_day_and_ending_day = f"| Available Days : {starting_day} to {ending_day}"
            # print(f"Pass name {pass_name} - {starting_day_and_ending_day}")
            if recommendations.strip() and recommendations.replace(" ",""):
                if pd.notna(recommendations) and str(recommendations)!="nan":
                    pass_name = f" {pass_name}  {recommendations}   " 
            age = row['age_allowed']
            jump_time = row['jump_time_allowed']
            # price = str(row['price']).replace("."," point ")
            price = str(row['price']).strip().replace('.', ' point ')
            introductory_pitch = row["pitch_introduction"]
            priority = row["pitch_priority"]
            availability = row["availability_days"]
            if int(priority)==1:
                most_popular_pass_prompt = f"""1. **[Always Present The {introductory_pitch} {jump_time} {pass_name_temp} for {age} First]:**
                - Calculate the day from selected date
                - Present the {introductory_pitch} {jump_time} {pass_name_temp} {recommendations} for {age} as the primary option:
                    - **Say Exactly:** "For our most popular pass, the {jump_time} {pass_name_temp} for {age}, you get {jump_time} of jump time for $[price of 90-Minute standard pass]."
                    - **Say Exactly Do not change any words:** "We have other jump passes as well - would you like to hear about those options or would you like to purchase the standard pass?"
                    - **Say Exactly Do not change any words:**"Just to let you know, memberships offer big savings compared to buying individual passes."""

            elif int(priority)==999:
                pass
            else:
                if availability == "always":
                    other_jump_passes_available_always +=f"""\n - Pass Name:{pass_name_temp} {recommendations} | Introductory Pitch:{introductory_pitch} | jump time:{jump_time} | ages for: {age} """

                else:
                    other_jump_passes_available_certain_days += f"""\n - Pass Name:{pass_name_temp}( {pass_name_temp} is available on certain days Please check schedule of hours of operations before mentioning {pass_name_temp}) {recommendations} | Introductory Pitch:{introductory_pitch} | jump time:{jump_time} | ages for: {age} """


                


            
            if not isinstance(pass_name, str) or pass_name.strip() == "":
                continue

            
            # Create detailed entry
            if int(priority)!=1:
                entry = f"- **{pass_name.strip()}** {starting_day_and_ending_day} | Price : ${price} | Ages Allowed: {age.lower()} | Jump Time: {jump_time}"
                pass_details.append(entry)
        summary.extend(pass_details)
        summary.append("")
    

    ### Jump passes which are not present in hours of operation
    sessions_not_available_for_jump_passes  = list(set(hours_jump_type_unique_values)- set(jump_passes_available_for_jumping) )
    
    ## case birthday package is available for jump type but jump pass is not available
    if len(sessions_not_available_for_jump_passes) >0:
        for not_available_jump_session in sessions_not_available_for_jump_passes:
            summary.append("\n")
            clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', not_available_jump_session).strip()
            clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
            section_title = clean_sched_name.replace(' ', ' ').title()
           
            summary.append(f"### {section_title} Jump Passes are not offered (Only Mention if user explicitly asks for it)")

    
    
    other_jump_passes_prompt += "\n" + other_jump_passes_available_always
    other_jump_passes_prompt += "\n" + other_jump_passes_available_certain_days 
    other_jump_passes_prompt += "\n" + other_jump_passes_donot_mention_until_asked
    
    ### end of jump passes which are not present in hours of operation
    jump_passes_information = {
        "jump_passes_info": "\n".join(summary),
        "most_popular_pass_prompt": most_popular_pass_prompt,
        "other_jump_passes_prompt" : other_jump_passes_prompt,
    }
      
    return jump_passes_information



async def extract_membership_info(df: pd.DataFrame, schedule_with_dict: Dict[str, str]) -> str:
    summary = []
    location = df['Location'].iloc[0].title()

    most_popular_membership = ""
    most_popular_membership_name = ""
    other_memberships_highlight = ""
    
    summary.append(f"### Membership Information \n")

    for _, row in df.iterrows():
        title = row.get('title',"na")
        title  = title.upper()
        schedule_with = row.get('schedule_with')
        activity_time = row.get('activity_time')
        features = row.get('features')
        valid_until = row.get('valid_until')
        if valid_until=="nan" or pd.isna(valid_until):
            valid_until_sentence = ""
        else:
            valid_until_sentence =f"Membership Valid Until : {valid_until}"
        price = row.get('price')
        parent_addon_price = row.get('parent_addon_price')
        subscription = row.get('Subscription')
        party_discount = row.get('party_discount')
        if party_discount=="nan" or pd.isna(party_discount):
            party_discount_sentence = ""
        else:
            party_discount_sentence =f"Party discounts : {party_discount}"
        pitch_priority = int(row.get('pitch_priority',"999"))
        pitch_introduction = row.get('pitch_introduction')

        most_popular_membership_name = title

        if pitch_priority==1:
            most_popular_membership=f"""
            ### STEP 1: [ALWAYS HIGHLIGHT *{title} - {pitch_introduction}* FIRST]
            - Lead with calmness and warmth about {title}
            - Make natural sentences out of this
            - Provide a SHORT sales highlight focusing ONLY on:
            * Activity time : {activity_time}
            * {party_discount_sentence}
            - DO NOT explain anything else at this stage
            - Use warmth language: "I'm excited to tell you about our incredible {title}!"

            ### STEP 2: ASK FOR INTEREST
            - With warm enthusiasm, ask: "Would you like to learn more about the {title} or hear about other options?"
            - Wait for user response

            ### STEP 3A: IF USER SAYS YES TO {title}:
            - construct natural sentences
            - Explain {title} details with calmness
            - Highlight ALL of the following:
            * Activity time : {activity_time}
            * Features : {features}
            * {party_discount_sentence}
            * Price : {price}
            * Parent addon price: {parent_addon_price}
            * {valid_until_sentence}
            * Subscription: {subscription}

            """
        else:
            if other_memberships_highlight == "":
                other_memberships_highlight = f"*{title} - {pitch_introduction}*"
            else:
                other_memberships_highlight +="," f"*{title} - {pitch_introduction}*"


        # Start composing the pass description
        pass_lines = []

        if pitch_priority!=1:

            if isinstance(title, str) and title.strip():
                pass_lines.append(f"**{title.strip()}**")

            # Schedule with values could be comma-separated list, so split and get info for each
            if isinstance(schedule_with, str) and schedule_with.strip():
                schedule_keys = [s.strip() for s in schedule_with.split(',')]
                

            if isinstance(activity_time, str) and activity_time.strip():
                pass_lines.append(f"Activity time: {activity_time.strip()}.")

            if isinstance(features, str) and features.strip():
                # Replace newlines with commas for smoother speech or display
                features_clean = features.replace('\n', ', ')
                pass_lines.append(f"Features: {features_clean}.")

            if isinstance(valid_until, str) and valid_until.strip():
                pass_lines.append(f"{valid_until_sentence.strip()}.")

            if isinstance(price, (int, float)):
                pass_lines.append(f"Price: ${str(price).strip().replace('.', ' point ')}.")

            if isinstance(parent_addon_price, str) and parent_addon_price.strip() and parent_addon_price.lower() != "not_allowed":
                # pass_lines.append(f"Parent add-on price: ${parent_addon_price.strip()}.")
                pass_lines.append(f"Parent add-on price: ${str(parent_addon_price).strip().replace('.',' point ')}.")

            if isinstance(subscription, str) and subscription.strip():
                pass_lines.append(f"Subscription type: {subscription.strip()}.")

            if isinstance(party_discount, str) and party_discount.strip():
                pass_lines.append(f"{party_discount_sentence.strip()}.")

            # Join the pass info with line breaks and add a blank line after each pass
            summary.append("\n".join(pass_lines) + "\n")

    other_memberships_highlight_step = f"""### STEP 3B: IF USER SAYS NO TO {most_popular_membership_name}
    - Share only the names of other available memberships:{other_memberships_highlight} .DO NOT explain anything else at this stage except for names of the memberships
    - Ask with warmth: "Which membership would you like me to explain in detail?"
    - Wait for their selection"""
    memberships_info_dict = {
        "most_popular_membership":most_popular_membership,
        "other_memberships_highlight" : other_memberships_highlight_step,
        "memberships_info":"\n".join(summary) 
    
    }
    return memberships_info_dict


async def extract_balloons_info(df_balloon, add_balloons_flag,is_booking_bot):
    
    balloon_prompt = ""
    other_balloon_packages = []
    ballon_packages_data = """"""
    note = ""
    if is_booking_bot=="yes":
       action_statement="""
        - Ask:"Which Balloon you want to add to [child name] birthday party?"
        *At any point If user wants to add a balloon package:
           Use function: save_balloon_package_new_booking()
           Parameters:
            - balloon_package: [user selected balloon package]
        

       """
    else:
        action_statement = f"""
        *At any point If user wants to book  balloon packages:

        **Step 1: You must say Exactly: regarding [Ballon Package selected by user] booking, Should I  connect you to one of our team member**
        **Step 2: If user says yes or similar confirmation**
            Use function: transfer_call_to_agent()
        - transfer_reason: "[Balloon Package selected by user] Booking Request"
        """
    if add_balloons_flag.lower() == 'yes':
        balloon_prompt = """### Start of Party Balloon Booking Flow ###\n
        - Present Balloon Packages in in a conversational way
        *Step 1:*check If user wants to add decorational Balloons to [child name Birthday Party**
        -Ask:"We have some amazing Balloon options that you can add to decorate your [child name] birthday celebration.Do you want to hear about Balloon Packages?"
        - If user says "yes" then proceed to *Step 2*

        *Step 1: Determine whether the user wants to add decorative balloons to [child name]'s birthday party*

        -Ask: "We have some amazing balloon options that can add a festive touch to [child name]'s birthday celebration. Would you like to hear about our Balloon Packages?"

        -If the user responds "yes", proceed to *Step 2*.
        
        """
        

        df_balloon = df_balloon.sort_values(by="call_flow_priority", ascending=True)
        # print("balloon")

        for _, row in df_balloon.iterrows():
            package_selected = row.get('package_name', "")
            if not is_valid(package_selected):   #skip empty rows early
                continue

            priority = row.get('call_flow_priority', "")
            package_inclusions = row.get('package_inclusions', "")
            price = str(row.get('price', "")).replace(".","point")
            discount = row.get('discount', "")
            note = row.get('note', "")
            promotional_pitch = row.get("promotional_pitch","")


            # Clean all fields safely
            package_selected = package_selected if is_valid(package_selected) else ""
            priority = priority if is_valid(priority) else ""
            package_inclusions = package_inclusions if is_valid(package_inclusions) else ""
            price = price if is_valid(price) else ""
            discount = discount if is_valid(discount) else ""
            promotional_pitch = promotional_pitch if is_valid(promotional_pitch) else ""

            if discount:
                discount = f"Discount : {discount}"
             
            note = note if is_valid(note) else ""

            if int(priority) == 1:
                balloon_prompt += f"""
                        #*STEP: 2* [Always Highlight the Most Popular {package_selected} First]*
                        -It includes:{package_inclusions}
                        -Ask user:"Would you like to hear more details about {package_selected} or hear about other Balloon packages too?"
                        - If user asks about other Balloon Packages Go to Present Other Party Balloons Options***:
                        
                          
             
                    """
                ballon_packages_data += f""" 
                *{package_selected}* :
                Ballons Included: {package_inclusions}
                {discount}
                Price: {price}
                    
                """
            else:  # priority 2, 3, etc.
                # Add to the ballon_packages_data string
                ballon_packages_data += f""" 
                *{package_selected}* :
                Ballons Included: {package_inclusions}
                {discount}
                Price: {price}
                    
                """
                # Add to the list of other packages
                other_balloon_packages.append(package_selected)

        if len(other_balloon_packages)>0:
            balloon_prompt += f"""\n # *STEP 3: Present Other Party Balloons Options*
                
                "Great question!  here are your other options:
                {",".join(other_balloon_packages)}
                If user wants to know about  any ballon package use this ballon data to explain interested ballon packages in a conversation flow:
                Ballon Packages:
                {ballon_packages_data}
                Balloon Add in Booking Process:
                {action_statement}

            """

        balloon_prompt += f""" \n
        ### Ballon Policy (Only if user asks):
        - Credits are not transferrable and non refundable and credits can only be used to buy ballon packages and are these credits cannot be used for Birthday party packages
        - {note}
        

        """
        balloon_prompt += f"""
            ### END of Party Balloon Booking Flow ###
        """


    return balloon_prompt




async def extract_group_bookings(df_group_rates,group_rates_flag):
    group_rates_prompt = ""
    Instruction = ""
    group_rates_data = """"""
    other_group_rate_packages = []
    if group_rates_flag.lower() == 'yes':
        group_rates_prompt = """### Start of Group Rates Booking Flow ###\n"""

        df_group_rates = df_group_rates.sort_values(by="call_flow_priority", ascending=True)
        # print("group rates")
        for _, row in df_group_rates.iterrows():
            group_package_selected = row.get('group_packages', "")
            
            priority = row.get('call_flow_priority', "")
            package_inclusion = row.get('package_inclusions')
            price_per_jumper = row.get('Flat_fee_jumper_price')
            minimum_jumpers = row.get('Minimum_jumpers', "")
            Instruction = row.get("Instruction","")

            # Clean all fields safely
            priority = priority if is_valid(priority) else ""
            package_inclusion = package_inclusion if is_valid(package_inclusion) else ""
            price_per_jumper = price_per_jumper if is_valid(price_per_jumper) else ""
            group_package_selected = group_package_selected if is_valid(group_package_selected) else ""
            minimum_jumpers = minimum_jumpers if is_valid(minimum_jumpers) else ""
            Instruction = Instruction if is_valid(Instruction) else ""
            # print("instruction : ",Instruction)
            if not is_valid(group_package_selected):   #skip empty rows early
                continue
            if int(priority) == 1:
                group_rates_prompt += f"""
                    #*STEP: 1* [Always Highlight the Most Popular {group_package_selected} First]*
                        "Perfect! Let me tell you about our most popular *{group_package_selected}*! #
                        - Explain the package inclusion and package details in a conversational way
                        - tell the user about {package_inclusion}
                        {Instruction}
                        - price per jumper {price_per_jumper} dollor (only mention when customer explicitly asks for it otherwise don't mention the price)
                        
                        *After explaining the {group_package_selected} details, ask:*
                        "Would you like to book this {group_package_selected} for your special celebration? or want to hear about other options?"

                        *If user shows interest in group rate packages:

                            **Step 1: You must say Exactly: regarding {group_package_selected} booking, Should I  connect you to one of our team member**
                            **Step 2: If user says yes or similar confirmation**
                                Use function: transfer_call_to_agent()
                            - transfer_reason: "Group rates package Booking Request"

                            *If NO - Present Other Options:*
                            - Continue to *STEP 2: Present Other Amazing Options*

                    """
            else:  # priority 2, 3, etc.
                # Add to the group_rates_data string
                group_rates_data += f""" 
                *{group_package_selected}* :
                - tell the user about {package_inclusion}
                {Instruction}
                - price per jumper {price_per_jumper} dollor (only mention when customer explicitly asks for it otherwise don't mention the price)
                    
                """
                # Add to the list of other packages
                other_group_rate_packages.append(group_package_selected)
                
        if len(other_group_rate_packages)>0:
            group_rates_prompt += f"""\n # *STEP 2: Present Other Amazing group rates Options*
                
                "Great question!  here are your other options:
                {",".join(other_group_rate_packages)}
                If user shows interest in any group rate package use this group rate data to explain interested group rate packages in a conversation flow:
                group rate Packages:
                {group_rates_data}

            """
        group_rates_prompt += f""" \n
        ### Group rate booking Policy:
        {Instruction}

        """
        group_rates_prompt += f"""
            ### END of Group Rate Booking Flow ###
        """


    return group_rates_prompt

async def extract_rental_facility_bookings(df_rental_facility,rental_facility_flag):
    rental_facility_prompt = ""
    Instruction = ""
    rental_facility_data = """"""
    # other_rental_facility_data_packages = []
    if rental_facility_flag.lower() == 'yes':
        rental_facility_transfer_step = "*Rental Facility Group Booking Transfer Procedure Step*"
        rental_facility_prompt = f"""### Start of Rental Facility Group Booking Flow ###\n
        - For Group Booking Rental Facility Packages are provided
        - Rental Facility group booking packages can be booked during normal business hours only. 
        - Donot mention any prices of rental packages and in case of any confusion go to {rental_facility_transfer_step}
        """

        # df_rental_facility = df_rental_facility.sort_values(by="call_flow_priority", ascending=True)
        print("rental facility")
        unique_groups = df_rental_facility["rental_group_name"].unique()
        for unique_group in unique_groups:
            df_rental_facility_group = df_rental_facility[df_rental_facility["rental_group_name"]==unique_group].copy()
            rental_facility_data += f""" \n
            *{unique_group} Rental Packages:*
            """
            for _, row in df_rental_facility_group.iterrows():

                rental_facility_selected = row.get('Rental_jumper_group', "")
                rental_inclusion = row.get('inclusions')
                price_per_jumper = row.get('per_jumper_price')
                minimum_jumpers = row.get('Minimum_jumpers', "")
                maximum_jumpers = row.get('maximum_jumpers',"")
                Instruction = row.get("Instruction","")

                # Clean all fields safely
                rental_inclusion = rental_inclusion if is_valid(rental_inclusion) else ""
                price_per_jumper = price_per_jumper if is_valid(price_per_jumper) else ""
                rental_facility_selected = rental_facility_selected if is_valid(rental_facility_selected) else ""
                minimum_jumpers = minimum_jumpers if is_valid(minimum_jumpers) else ""
                maximum_jumpers = maximum_jumpers if is_valid(maximum_jumpers) else f"Donot say: if user inquired about maximum jumpers confirm from facility by Transfering the call by going to:{rental_facility_transfer_step} "
                
                Instruction = Instruction if is_valid(Instruction) else ""
                # print("instruction : ",Instruction)
                if not is_valid(rental_facility_selected):   #skip empty rows early
                    continue
                rental_facility_data += f""" \n 
                ** {rental_facility_selected} **
                - Construct Natural Sentences
                - Minimum number of jumpers eligibility to get rental facility:{minimum_jumpers}
                -Maximum number of jumpers eligibility to get rental facility: {maximum_jumpers}
                - Inclusion: {rental_inclusion}
                -Eligibility criteria: {rental_facility_selected} package is only available for groups of {unique_group}.
                """
            
            

       

        rental_facility_prompt += f""""\n
        *Step 1: Ask : "For how many jumpers you want to group booking"*
         - Tell relevant packages names and its inclusion depending upon which group does [user said number of jumpers lie in] from below Rental Facility Group Packages data:
         Rental Facility Group Booking Packages:
         {rental_facility_data}
         

        -*If user shows interest in booking Rental Facility packages the go to {rental_facility_transfer_step}
        ---
        
        {rental_facility_transfer_step}
        **Step 1: You must say Exactly: regarding [user query about rental facility group booking package], Should I  connect you to one of our team member**
        **Step 2: If user says yes or similar confirmation**
            Use function: transfer_call_to_agent()
        - transfer_reason: "Rental Facility [user query about rental facility group booking package]"

        ---

        
        """
                      
        rental_facility_prompt += f"""
            ### END of Rental Facility Booking Flow ###
        """


    return rental_facility_prompt

async def extract_items_info(df: pd.DataFrame,add_shirts_while_booking) -> str:
    summary = ["### Available Items and Prices \n"]

    for _, row in df.iterrows():
        item = row.get('item')
        price = row.get('price')
        
        if str(item).strip()!="t-shirt":
            if isinstance(item, str) and item.strip() and isinstance(price, str) and price.strip():
                # summary.append(f"- {item.strip()}: {price.strip()}.")
                summary.append(f"- {item.strip()}: {str(price).strip().replace('.',' point ')}.")
            elif isinstance(item, str) and item.strip() and (isinstance(price, (int, float))):
                # summary.append(f"- {item.strip()}: ${price}.")
                summary.append(f"- {item.strip()}: ${str(price).strip().replace('.',' point ')}.")

    return " \n ".join(summary)

async def extract_discount_info(df: pd.DataFrame) -> str:
    summary = ["\n"]

    for _, row in df.iterrows():
        discount = row.get('discount_type')

        if isinstance(discount, str) and discount.strip():
            summary.append(f"- {discount.strip()}.")

    return "\n".join(summary)

async def extract_faqs_for_llm(df: pd.DataFrame) -> str:
    summary = []
    
    grouped = df.groupby('question_type')

    for category, group in grouped:
        summary.append(f"### {category.title()} FAQs:\n")
        for _, row in group.iterrows():
            question = row.get("question", "").strip()
            answer = row.get("answer", "").strip()

            if question and answer:
                summary.append(f"**Question:** {question}\n**Answer:** {answer}.\n")

    return "\n".join(summary)

async def extract_terminology_info(df: pd.DataFrame) -> str:
    """
    Extracts Sky Zone terminology definitions in an LLM-friendly format.
    Ignores empty or missing values.
    """
    summary = ["\n"]
    for _, row in df.iterrows():
        term = row.get('term')
        definition = row.get('definition')
        if isinstance(term, str) and term.strip() and isinstance(definition, str) and definition.strip():
            summary.append(f"- **{term.strip()}**: {definition.strip()}.")
    return "\n".join(summary)

async def extract_policies_llm_friendly(df: pd.DataFrame) -> str:
    # Drop the location column
    
    df = df.drop(columns=["Location"], errors="ignore")
    
    # Capitalize and format policy types
    df['policy_type'] = df['policy_type'].str.title()

    # Clean up whitespaces/newlines in details
    df['details'] = df['details'].str.replace(r'\s+', ' ', regex=True).str.strip()

    # Build LLM-friendly formatted string
    output = "\n"
    for _, row in df.iterrows():
        output += f"**{row['policy_type']}**:\n{row['details']}.\n\n"

    return output.strip()


### birthday party prompt


async def collect_customer_details_prompt(skip_customer_details_in_prompt,customer_first_name,customer_last_name,customer_email,data_collection_next_step):
    
    # print(skip_customer_details_in_prompt,customer_first_name,customer_last_name,customer_email,data_collection_next_step)
    data_collection_first_step = f"""
    Step 1: ACKNOWLEDGE BIRTHDAY CHILD
        - Say:"I already have [child's name] as our birthday star! Now I need some details from you to complete the booking."
    """
    first_name_collection_additional_instruction = f"""
    - Donot Proceed to *LAST NAME COLLECTION Step* Until user has confirmed their first name*

    """
    last_name_collection_additional_instruction = f"""
    - Donot Proceed to *EMAIL COLLECTION Step* Until user has confirmed their last name*

    """
    email_collection_additional_instruction = f"""
    - Donot Proceed to *PHONE NUMBER COLLECTION Step* Until user has confirmed their email*

    """
    phone_number_collection_additional_instruction = f"""
    - Donot Proceed to *EMAIL VERIFICATION FOR BOOKING Step* Until phone number collection is complete*

    """
    
    
    if skip_customer_details_in_prompt==False:
        
        data_collection_step = f"""

            {data_collection_first_step}
            ---
            *STEP 2: FIRST NAME COLLECTION:*

                   - Say exactly:"Is {customer_first_name} your first name?"
                    *step 2.1: Confirm the first name from user*
                    *step 2.2: If user confirms their first name move to 'step 2.3'*
                    *step 2.3: use function : save_first_name()*
                            parameters : first_name:[user first name]
                    *step 2.4: If user does not confirm their first name ->
                        Step 2.4.1: *Say exactly* "What's your first name? Please spell it very slowly, letter by letter. For example, A for Alpha, B for Bravo, and so on."
                        Step 2.4.2: LISTEN for response
                        Step 2.4.3: IMMEDIATE REPEAT BACK: "I heard [name]. Is that correct?"
                        Step 2.4.4: If NO or if name sounds unclear:
                                "Let me get that right. Can you spell your first name for me, letter by letter? For example, A for Alpha, B for Bravo, and so on."
                        Step 2.4.5: SPELL BACK using NATO: 
                                "So that's [Alpha-Bravo-Charlie]. Is that correct?"
                        Step 2.4.6: LISTEN for user response
                                - If user says "correct", "yes", "right", "that's right" →
                                Execute function: save_first_name(first_name: [confirmed_name])
                                Say: "Perfect! I've got your first name."
                        Step 2.4.7: LISTEN for user response  
                                - If user says "incorrect", "no", "wrong", "that's not right" → 
                                Return to Step 2.4.4
                        {first_name_collection_additional_instruction}
            ---            
            * STEP 3: LAST NAME COLLECTION *
                   - Say:"Is {customer_last_name} your last name?"
                    *step 3.1: Confirm the last name from user*
                    *step 3.2: If user confirms their last name move to 'step 3.3'*
                    *step 3.3: use function : save_last_name()*
                            parameters : last_name:[user last name]
                    *step 3.4: If user does not confirm their fist name ->
                        Step 3.4.1: *Say exactly* "And what's your last name? Please spell it very slowly, letter by letter. For example, A for Alpha, B for Bravo, and so on."
                        Step 3.4.2: LISTEN for response
                        Step 3.4.3: IMMEDIATE REPEAT BACK: "I heard [last name]. Is that correct?"
                        Step 3.4.4: If NO or if name sounds unclear:
                                "Let me make sure I get this right. Can you spell your last name for me, letter by letter? For example, A for Alpha, B for Bravo, and so on."
                        Step 3.4.5: SPELL BACK using NATO:
                                "So that's [Alpha-Bravo-Charlie-Delta]. Is that correct?"
                        Step 3.4.6: LISTEN for user response
                                - If user says "correct", "yes", "right", "that's right" → 
                                Execute function: save_last_name(last_name: [confirmed_name])
                                Say: "Great! your Last name is confirmed."
                        Step 3.4.7: LISTEN for user response  
                                - If user says "incorrect", "no", "wrong", "that's not right" → 
                                Return to Step 3.4.4
                        {last_name_collection_additional_instruction}   
            ---
            *Step 4: Email Collection for booking*

                *Step 4.1: "Read the email address {customer_email} very slowly character by character when confirming. Break down the email like this: For 'john.doe@example.com' say 'j o h n dot d o e at e x a m p l e dot c o m'. Ask: 'Should I use this email address to send [child's name]'s party confirmation?'"*
                - If user says "correct", "yes", "right", "that's right" → 
                        Execute: save_user_email(user_email: [confirmed_email])
                        → PROCEED TO STEP 5
                    
                - If user says "incorrect", "no", "wrong", "that's not right" →
                - Ask for alternate email address

                Step 4.2: Say exactly: "What's the best email address to send [child's name]'s party confirmation to? Please spell it out letter by letter for me. For example, A for Alpha, B for Bravo, and so on."

                Step 4.3: LISTEN and CAPTURE each character that user spells out

                Step 4.4: IMMEDIATE REPEAT BACK using NATO phonetic alphabet + symbols:
                        Say: "Let me confirm that email address: [Alpha-Bravo-Charlie at Delta-Echo-Foxtrot dot Charlie-Oscar-Mike]. Is that correct?"

                MANDATORY SYMBOL PRONUNCIATIONS:
                - @ = *Say exactly* "at"
                - . = "dot" 
                - . = "period"
                - _ = "underscore"  
                - - = "dash"

                Step 4.5: LISTEN for user response
                        - If user says "correct", "yes", "right", "that's right" →
                        - Convert the confirmed spoken email into a valid email format by replacing words with symbols:

                        - Replace " at " → "@"

                        - Replace " dot " or " period " → "."

                        - Remove extra spaces between characters

                        - Combine letters and numbers into a single word (e.g., "j o h n" → "john")

                        - Validate the final format:

                        - It must contain one @ symbol and a valid domain ending such as .com, .net, .org, etc.

                        - If invalid, politely ask the user to repeat it.

                        - Once valid, execute:  
                        Execute: save_user_email(user_email: [confirmed_email])
                        Say: "Perfect! Email address saved."
                        → PROCEED TO STEP 5
  
                        - If user says "incorrect", "no", "wrong", "that's not right" →
                        Say exactly: "Would you like me to send you a text message where you can reply with your email address?"

                Step 4.6: LISTEN for user response
                        - If user agrees to SMS (says "yes", "sure", "okay", "send text") →
                        Say exactly: "Great, I'll send a text to your current number. Please reply with your email address. Once you have sent the SMS, let me know. Message and data rates may apply. You can find our privacy policy and terms and conditions at purpledesk.ai."
                        Execute function: send_sms_for_email()

                Step 4.7: WAIT for user to say "I have sent you the text message" OR "I replied to your text" OR similar confirmation
                        THEN Execute function: check_sms_received_containing_user_email()
                        Say: "Thank you! I've received your email address."
                        → PROCEED TO STEP 5

                {email_collection_additional_instruction}
                ---


            *Step 5: PHONE NUMBER COLLECTION*
                ### Instruction
                - ALWAYS verify the ALTERNATE NUMBER

                Step 5.1: "For contact purposes, should we use your current phone number, or would you prefer to give me a different number?"

                SCENARIO A - ALTERNATE NUMBER:
                Step 5.2: "Please give me the 10-digit phone number, including area code."
                Step 5.3: REPEAT BACK IN GROUPS: 
                        "I have [Five-Five-Five] [One-Two-Three] [Four-Five-Six-Seven]. Is that correct?"
                Step 5.4: If YES → Execute: save_user_phone_number(phone_number: [confirmed_number])
                Step 5.5: If NO → "Let me get those digits again, please say them slowly."

                SCENARIO B - CURRENT NUMBER:
                Step 5.6: "Perfect! We'll use your current number for the party details."
                → PROCEED TO STEP 6

            {phone_number_collection_additional_instruction}
                        
            ---
            
            * Step 6: EMAIL VERIFICATION FOR BOOKING *
                Step 6.1: Say exactly: "Now, I'll send a text to your current phone number with your email address for verification. If the email address is incorrect, please reply with the correct one."
                    - Execute function: send_sms_for_email()
                
                Step 6.2: LISTEN for user response
                    - If user confirms email is correct (e.g., "yes it's correct", "my email is correct", "that's right", or similar confirmation):
                        → Say: "Great! Your email is confirmed."
                        → Execute function: handle_email_confirmation_from_sms_voice()
                        → SKIP remaining email verification steps
                        → Go directly to *Package Recap for [child's name]:* and then proceed to {data_collection_next_step}
                    
                    - If user says "I have sent you the text message" OR "I replied to your text" OR "I have sent my email to you" OR similar:
                        → Execute function: check_sms_received_containing_user_email()
                        → Say: "Thank you! I've received your email address."
                        → Go to *Package Recap for [child's name]:* and then proceed to {data_collection_next_step}
            ---
                
        """
    else:
        data_collection_step = f"""


            
            {data_collection_first_step}
            ---
            *STEP 2: FIRST NAME COLLECTION*
                *INSTRUCTION*
                - ALWAYS reconfirm user first name
                
                

                Step 2.1: *Say exactly* "What's your first name? Please spell it very slowly, letter by letter. For example, A for Alpha, B for Bravo, and so on."
                Step 2.2: LISTEN for response
                Step 2.3: IMMEDIATE REPEAT BACK: "I heard [name]. Is that correct?"
                Step 2.4: If NO or if name sounds unclear:
                        "Let me get that right. Can you spell your first name for me, letter by letter? For example, A for Alpha, B for Bravo, and so on."
                Step 2.5: SPELL BACK using NATO: 
                        "So that's [Alpha-Bravo-Charlie]. Is that correct?"
                Step 2.6: LISTEN for user response
                        - If user says "correct", "yes", "right", "that's right" →
                        Execute function: save_first_name(first_name: [confirmed_name])
                        Say: "Perfect! I've got your first name."
                Step 2.7: LISTEN for user response  
                        - If user says "incorrect", "no", "wrong", "that's not right" → 
                        Return to Step 2.4
                {first_name_collection_additional_instruction}
            ---
            * STEP 3: LAST NAME COLLECTION *
                *INSTRUCTION*
                - ALWAYS reconfirm user last name

                Step 3.1: *Say exactly* "And what's your last name? Please spell it very slowly, letter by letter. For example, A for Alpha, B for Bravo, and so on."
                Step 3.2: LISTEN for response
                Step 3.3: IMMEDIATE REPEAT BACK: "I heard [last name]. Is that correct?"
                Step 3.4: If NO or if name sounds unclear:
                        "Let me make sure I get this right. Can you spell your last name for me, letter by letter? For example, A for Alpha, B for Bravo, and so on."
                Step 3.5: SPELL BACK using NATO:
                        "So that's [Alpha-Bravo-Charlie-Delta]. Is that correct?"
                Step 3.6: LISTEN for user response
                        - If user says "correct", "yes", "right", "that's right" → 
                        Execute function: save_last_name(last_name: [confirmed_name])
                        Say: "Great! your Last name is confirmed."
                Step 3.7: LISTEN for user response  
                        - If user says "incorrect", "no", "wrong", "that's not right" → 
                        Return to Step 3.4
                {last_name_collection_additional_instruction}
            ---
            *Step 4: Email Collection for booking* 
                *INSTRUCTION*
                - ALWAYS reconfirm user email address

                Step 4.1: Say exactly: "What's the best email address to send [child's name]'s party confirmation to? Please spell it out letter by letter for me. For example, A for Alpha, B for Bravo, and so on."

                Step 4.2: LISTEN and CAPTURE each character that user spells out

                Step 4.3: IMMEDIATE REPEAT BACK using NATO phonetic alphabet + symbols:
                        Say: "Let me confirm that email address: [Alpha-Bravo-Charlie at Delta-Echo-Foxtrot dot Charlie-Oscar-Mike]. Is that correct?"

                MANDATORY SYMBOL PRONUNCIATIONS:
                - @ = *Say exactly* "at"
                - . = "dot" 
                - . = "period"
                - _ = "underscore"  
                - - = "dash"

                Step 4.4: LISTEN for user response
                        - If user says "correct", "yes", "right", "that's right" →
                        - Convert the confirmed spoken email into a valid email format by replacing words with symbols:

                            - Replace " at " → "@"

                            - Replace " dot " or " period " → "."

                            - Remove extra spaces between characters

                            - Combine letters and numbers into a single word (e.g., "j o h n" → "john")

                            - Validate the final format:

                            - It must contain one @ symbol and a valid domain ending such as .com, .net, .org, etc.

                            - If invalid, politely ask the user to repeat it.

                        - Once valid, execute: 
                            save_user_email(user_email: [confirmed_email])
                        Say: "Perfect! Email address saved."
                        → PROCEED TO STEP 5

                        - If user says "incorrect", "no", "wrong", "that's not right" →
                        Say exactly: "Would you like me to send you a text message where you can reply with your email address?"

                Step 4.5: LISTEN for user response
                        - If user agrees to SMS (says "yes", "sure", "okay", "send text") →
                        Say exactly: "Great, I'll send a text to your current number. Please reply with your email address. Once you have sent the SMS, let me know. Message and data rates may apply. You can find our privacy policy and terms and conditions at purpledesk.ai."
                        Execute function: send_sms_for_email()

                Step 4.6: WAIT for user to say "I have sent you the text message" OR "I replied to your text" OR similar confirmation
                        THEN Execute function: check_sms_received_containing_user_email()
                        Say: "Thank you! I've received your email address."
                        → PROCEED TO STEP 5
                
                {email_collection_additional_instruction}
                
                ---

                        
            *Step 5: PHONE NUMBER COLLECTION*
                ### Instruction
                - ALWAYS verify the ALTERNATE NUMBER

                Step 5.1: "For contact purposes, should we use your current phone number, or would you prefer to give me a different number?"

                SCENARIO A - ALTERNATE NUMBER:
                Step 5.2: "Please give me the 10-digit phone number, including area code."
                Step 5.3: REPEAT BACK IN GROUPS: 
                        "I have [Five-Five-Five] [One-Two-Three] [Four-Five-Six-Seven]. Is that correct?"
                Step 5.4: If YES → Execute: save_user_phone_number(phone_number: [confirmed_number])
                Step 5.5: If NO → "Let me get those digits again, please say them slowly."
                
                SCENARIO B - CURRENT NUMBER:
                Step 5.6: "Perfect! We'll use your current number for the party details."
                → PROCEED TO STEP 6
            {phone_number_collection_additional_instruction}

            ---
                    

        
            *Step 6: EMAIL VERIFICATION FOR BOOKING*
                Step 6.1: Say exactly: "Now, I'll send a text to your current phone number with your email address for verification. If the email address is incorrect, please reply with the correct one."
                    - Execute function: send_sms_for_email()
                
                Step 6.2: LISTEN for user response
                    - If user confirms email is correct (e.g., "yes it's correct", "my email is correct", "that's right", or similar confirmation):
                        → Say: "Great! Your email is confirmed."
                        → SKIP remaining email verification steps
                        → Go directly to *Package Recap for [child's name]:* and then proceed to {data_collection_next_step}
                    
                    - If user says "I have sent you the text message" OR "I replied to your text" OR "I have sent my email to you" OR similar:
                        → Execute function: check_sms_received_containing_user_email()
                        → Say: "Thank you! I've received your email address."
                        → Go to *Package Recap for [child's name]:* and then proceed to {data_collection_next_step}

            ---

        
        """
    # print(skip_customer_details_in_prompt,customer_first_name,customer_last_name,customer_email,step_counter)
    # print(data_collection_step)
    return data_collection_step


async def provide_editing_instructions(is_edit_bot,existing_booking_details,edit_food_prompt,max_step_counter_edit,minimum_jumpers_party,birthday_mappings,birthday_packages_data):
    prompt = """"""
    base_prompt = """## *ALREADY BOOKED BIRTHDAY PARTY AND WANTS CHANGES IN ALREADY MADE BIRTHDAY PARTY BOOKING*
                    *If customer has already made a party reservation  or wants to add-on food or make changes to their already booked birthday party package:*

                    *Examples already reservered party booking scenarios (These scenarios are different from new booking.In new bookings user can make changes because you have the ability to create new birthday bookings):*
                    - "I already have a booking and want to add food"
                    - "I need to make changes to my birthday party booking (already reserved)"
                    - "Can I add more food to my already reserved party package?"
                    - "I want to modify my already reserved birthday party reservation"
                    - "I had a party booked and need to add items"
                    - "I want to upgrade my already booked/reserved  birthday party package?"""
    
    cancel_prompt = """"""
    if is_edit_bot=="no" or not existing_booking_details:
        prompt = f"""
                    {base_prompt}
                    Step 1.1: Say exactly: Regarding your [already booked party modification request], Should I connect you with one of our team member
                    Step 1.2: If user says yes or similar confirmation to transfer**
                    Use function: transfer_call_to_agent()
                    - transfer_reason: "Birthday Party Modification"

                    *Skip all other steps and transfer immediately for already booked Party booking modifications.*
                    ---
                    """
    else:
        
        user_selected_birthday_package = existing_booking_details['party_package']
        birthday_other_options_other_then_user_selection =",".join( (birthday_mappings.pop(user_selected_birthday_package)).keys() )    
        

        prompt = f"""
            {base_prompt}

            ## INSTRUCTIONS
            - Execute the relevant step according to the user query
            - *Always confirm current booking details before making changes*
            - Use exact phrases where specified
            - Wait for user confirmation before proceeding with changes

            ## EXAMPLE TRIGGERS
            - Example-1: "I want to change the booking date" EXECUTE *CHANGE BOOKING DATE OF ALREADY MADE BOOKING STEP*
            - Example-2: "I want to change the time/booking time"  Execute *BOOKING TIME CHANGE OF ALREADY MADE BOOKING*  
            - Example-3: "I want to change the birthday package or I want to upgrade from Basic to EPIC or I want to downgrade from MEGA VIP to EPIC" → Execute *CHANGE BIRTH DAY PARTY PACKAGE OF ALREADY MADE BOOKING STEP*
            - Example-4: "I want to add, remove or reduce jumpers" → Execute CHANGE NUMBER OF JUMPERS OF ALREADY MADE BOOKING STEP **
            - Example-5: "I want to add extra food, drinks or party tray or addons" → EXECUTE HANDLE FOOD / DRINKS / PARTY TRAYS / ADDONS CHANGES STEP
            
            ## CHANGE BOOKING DATE OF ALREADY MADE BOOKING
            *When user query is related to changes in booking date:*

            1. *Say Exactly:* "So your birthday party was arranged for {existing_booking_details['booking_date']} with us. Would you like to change your booking date?"

            2. *If user confirms* ("correct", "yes", "right", "that's right"):
                - Collect the new date from user
                - Execute: identify_day_name_from_date_already_made_booking() 
                - Parameters: new_booking_date:[YYYY-MM-DD format]
            3. *Collect Time*
                - "What time works best for the party?"
                - If user explicitly ask which slots are available for [specific day or date they mentioned earlier]?
                    Use function : check_existing_booking_available_time_slots()
                    parameters: date : YYYY-mm-dd format
            4. *Check Availability*
                Use function: check_party_room_availability_for_existing_booking()
                Parameters:
                - party_time: 24 Hour Format  
                Scenario: when party room is available for the time slot
                -If room is available: *Proceed to Step Completion*
                Scenario: when party room is not available for the time slot or user picks alternate time slot
                    step 1:If party room is not available: "I'm sorry, that time slot isn't available for [child's name]'s party. Let me check what times we have open..." [Present alternative time slots]
                    step 2: If user picks alternate time slot use function: check_party_room_availability_for_existing_booking()
                        - party_time: 24 Hour Format 
                        - add_number_of_jumper: [{int(minimum_jumpers_party)+int(existing_booking_details['package_additional_jumper_quantity'])}]

            5. *Proceed to Step Completion*


            ## BOOKING TIME CHANGE OF ALREADY MADE BOOKING
            *When user query is related to changes in booking time:*

            1. *Say Exactly:* "So your birthday party was scheduled for {existing_booking_details['session_time']} on {existing_booking_details['booking_date']}. Would you like to change your booking time?"

            2. *If user confirms:*
            *Collect Time*
                - "What time would you prefer for the party?"
                - If user explicitly ask which slots are available for [specific day or date they mentioned earlier]?
                    Use function : check_existing_booking_available_time_slots()
                    parameters: date : YYYY-mm-dd format
            3. *Check Availability*
                Use function: check_party_room_availability_for_existing_booking()
                Parameters:
                - party_time: 24 Hour Format  
                Scenario: when party room is available for the time slot
                -If room is available: *Proceed to Step Completion*
                Scenario: when party room is not available for the time slot or user picks alternate time slot
                    step 1:If party room is not available: "I'm sorry, that time slot isn't available for party. Let me check what times we have open..." [Present alternative time slots]
                    step 2: If user picks alternate time slot use function: check_party_room_availability_for_existing_booking()
                        - change_party_time: 24 Hour Format
                        - add_number_of_jumper: [{int(minimum_jumpers_party)+int(existing_booking_details['package_additional_jumper_quantity'])}]


            4. *Proceed to Step Completion*
        ---
        ## CHANGE BIRTH DAY PARTY PACKAGE OF ALREADY MADE BOOKING STEP
            *When user query is related to changes in package/service:*

            Step 1. *Say Exactly:* "Your current booking includes the {user_selected_birthday_package} package. Would you like to change to a different package?"
            Step 2. If user says yes or similar confirmation
                    - Present other Bithday options to user in a converational way
                    - Just Highlight the Other birthday options names provided below:{birthday_other_options_other_then_user_selection}
                    - If user asks about details of particular package use this data:
                        {birthday_packages_data}
            Step 3.Ask user to select a birthday package
                  Step 1: *Ask user: Are you sure you want to [Already Selected Birthday Party Package] to [Newly selected Birthday Package]*
                  Step 2: If user says yes or similar confirmation
                          - Execute: change_existing_party_package()
                          - Parameters:-------

        ---
        ## CHANGE NUMBER OF JUMPERS OF ALREADY MADE BOOKING
            *When user query is related to adding more jumpers:*

            Step 1. *Say Exactly:* "Your current booking includes {user_selected_birthday_package} with {int(minimum_jumpers_party)+int(existing_booking_details['package_additional_jumper_quantity'])} jumpers."

            Step 2. "Ask user to provide Number of Jumpers that user will have for the party"

                *Step 2.1: When user provides number of Jumpers*
                 - Step 1: *Ask user: Are you sure you want to [Already Selected    Number of Jumpers] to [Newly selected Number of Jumpers]*
                  - Step 2: If user says yes or similar confirmation
                          - Use function: change_already_made_booking_number_of_jumpers()
                          - Parameters:number_of_jumpers:[User selected number of jumpers]


            3. *Proceed to Step Completion*

        ---
        ### HANDLE FOOD / DRINKS / PARTY TRAYS / ADDONS CHANGES STEP
        {edit_food_prompt}



        ----

        
                      


        """
    return prompt

async def provide_direct_booking_scenario(is_booking_bot, booking_process_instructions,minimum_jumpers_party):
    prompt = """"""

    if is_booking_bot=="yes":
        
        collect_birthday_package_step = booking_process_instructions['collect_birthday_party_package_interest_instructions']
        
        collect_birthday_package_step = collect_birthday_package_step.format(
            next_step = """- **Only proceed to *Collect Birthday Child's Name For New Booking Step* after Birthday party package is confirmed and saved**"""
        )

        collect_child_name_step = booking_process_instructions['collect_child_name_instructions']

        collect_child_name_step = collect_child_name_step.format(
            next_step = """- **Only proceed to *Collect the Date For New Booking Step* after child's name is saved**"""
        )

        collect_date_step = booking_process_instructions['date_collection_step']

        collect_date_step = collect_date_step.format(
            # next_step = """ - **Only proceed to *Collect Time For New Booking Step* after date is confirmed**"""
            next_step_name = """*Collect Time For New Booking Step*"""
        )

        collect_time_of_booking_step = booking_process_instructions['collect_time_of_booking_step']
        collect_time_of_booking_step = collect_time_of_booking_step.format(
            next_step = """ - **Only proceed to *Collect Number of Jumpers For New Booking Step* after party time is saved**""",
            
            next_step_name = """*Collect Number of Jumpers For New Booking Step*"""
        )

        collect_number_of_jumpers_step = booking_process_instructions['collect_number_of_jumpers_instructions']
        collect_number_of_jumpers_step = collect_number_of_jumpers_step.format(
            minimum_jumpers_party = minimum_jumpers_party,
            next_step = """
                    - **Only proceed to *Food Drinks and Addons Selection For New Booking* after number of jumpers is saved**
            """


        )

        prompt = f"""
            ## *DIRECT NEW BOOKING SCENARIO*
            *If user directly asks to book a specific birthday party by name (e.g., "I want to book an epic birthday party package" or "Book me a basic birthday party package"):*

            *Step 1: Collect COLLECT BIRTHDAY PARTY PACKAGE For New Booking*
            {collect_birthday_package_step}
            ---
            

            *Step 2: Collect Birthday Child's Name For New Booking*
            {collect_child_name_step}

            ---
            
            *Step 3: Collect the Date For New Booking*
            {collect_date_step}

            ---

            *Step 4: Collect the Time For New Booking*
            {collect_time_of_booking_step}
           
            ---
            *Step 5: Collect Number of Jumpers For New Booking*
             {collect_number_of_jumpers_step}
            ---


        """
    else:
        prompt = """
            ## Direct Booking Scenario
            If the user directly asks to book a specific birthday party by name  
            (e.g., “I want to book an Epic Birthday Party Package” or “Book me a Basic Birthday Party Package”):
            **Step 1: You must say Exactly: Regarding [user booking query] I will connect you to our team member**
            **Step 2: Confirm and Transfer**
                Use function: transfer_call_to_agent()
            - transfer_reason: "Direct Booking Request"

            **Note:**  
            Skip the full 6-step process for direct booking requests and go straight to agent transfer.
            """

    return prompt


async def get_info_bot_booking_process_instructions(birthday_party_info,cancel_birthday_party_before_party_date_days,skyzone_food_drinks_info,minimum_deposit_required_for_booking):
    prompt = f"""
        ### 6-Step Birthday Party Sales Process

        If the user says they are interested in booking a birthday party package (e.g., "book a party", "I want to book a birthday party package", "I want to reserve a birthday party package"):

        **Step 1: Ask user "You want to book a birthday party package or get general information about the packages?"**
        

        If the user wants to **book a package**:
            Step 1.1: Say exactly: Regarding your [booking request], Should I connect you with one of  our team member
            Step 1.2: If user says yes or similar confirmation to transfer**
            → Use function: `transfer_call_to_agent()`
            - `transfer_reason`: "Direct Booking Request"
        - Skip the remaining sales process and go straight to agent transfer.

        If the user wants **general information**, Go to *Step 2: Identify Date or Day*.

        ---

        ## Step 2: Identify Date or Day on which user wants to book the party *Mandatory Step*

        Ask when the customer wants to celebrate the birthday.

        At any point, if the user specifies a date like “today”, “tomorrow”, or “on 2025-06-17”,  
        convert it to a day name using:
        - use function: identify_day_name_from_date_new_booking()
        - Parameters: booking_date: [YYYY-mm-dd format]

        **If the message already includes a day/date:**
        - Acknowledge: “So you're planning to celebrate on [day/date]!”
        - Check schedule availability.
        - Move to Step 3.

        **If not:**
        - Ask: "When you would  like to book the [PACKAGE NAME]?"
        - Wait for the response, acknowledge it, and check availability.
        - Don't proceed to Step 3 until the date is confirmed.

        **Skip the question if user says:**
        - “Do you have a birthday party package for Saturday?”
        - “What's available this weekend?”
        - “Can I book for tomorrow?”
        - “I want to celebrate on Friday.”

        **Ask the question if user says:**
        - “Do you have birthday party packages?”
        - “What birthday party packages are available?”
        - “I'm interested in your birthday packages.”

        {birthday_party_info['most_popular_birthday_package_prompt']}

        *If YES - Close the Sale:*
        - Move directly to *STEP 6: Securing the Booking*

        *If NO - Present Other Options:*
        - Continue to *STEP 4: Present Other Amazing Options*

        ---

        ## *STEP 4: Present Other Amazing Options*
        Only if they ask about other packages Check Availability of Party packages from  Schedule for the Calculated Day from Date
        - Only mention those Birthday Party packages that are available for the calculated day
        "Great question! Based on your date, here are your other options:

        {birthday_party_info['other_birthday_packages_prompt']}

        *When customer asks for details of any specific birthday party package:*
        - Explain the duration breakdown (jump time + party room time or party space time or open air time depending upon the package)
        - Focus on explaining minimum jumpers,Food and drinks included in Package, paper goods, skysocks, Desserts and Cakes Policy, Outside Food Fee(Policy), Birthday Package Perks,additional hour if any,Additional Jumper Cost clearly
        - Reference current birthday party package data for all specifics

        ---

        ## *STEP 5: Package Selection & Personalization*
        Help them choose with calmness

        "What package sounds like the perfect fit for your special celebration?

        After a birthday party package is chosen move to *STEP 6: Securing the Booking*

    

        ---

        ## *STEP 6: Securing the Booking*
        Close with care and clear expectations

        "Great you've chosen [SELECTED PACKAGE]! Now, let me walk you through how we secure this amazing celebration for you.

        *Deposit for Securing your booking:*
        - We require a {minimum_deposit_required_for_booking} deposit to hold your party date
        - You'll have 24 hours to complete this deposit
        - This secures everything we've discussed today

         **Package Recap:**  
        Summarize only:
        - Party Package Name  
        - Price  
        - Additional Jumper Cost  

        **Cancellation Policy (only if asked):**
        
        *Our Cancellation Policy* (explained with empathy) [Only Explain Birthday party cancellation policy if user ask for it]:
        I know life can be unpredictable sometimes, so here's our policy:
        - Cancel {cancel_birthday_party_before_party_date_days}+ days before: Full refund to your original payment method
        - Cancel less than {cancel_birthday_party_before_party_date_days} days before: Deposit is non-refundable (we'll have already prepared everything for your party)

        *Pro Tips for Your Party:*
        - Arrive 15-30 minutes early (the birthday calmness is contagious!)

        Ask the user:
        Are you ready to make this birthday absolutely unforgettable? Should we move forward with securing your booking?"

        ---

        ## *BOOKING CONFIRMATION & TRANSFER*

        When customer confirms booking:

        Step 1:*Use function: transfer_call_to_agent()*
        Use function: transfer_call_to_agent()
        - transfer_reason: "[user selected party package] Reservation ,Date for Booking: [Date for Party Booking]"

        ---

        ## *FOOD & DRINK GUIDELINES*

        {skyzone_food_drinks_info["food_drinks_prompt"]}

        ---

        ## PRICING LOGIC FOR FOOD

        Standard Birthday Party Packages (Epic Birthday Party Package, Mega VIP Birthday Party Package, Little Leaper Birthday Party Package, Glow Birthday Party Package):
        Included:
        - Base package includes:
            2 pizzas
            2 drinks
            for up to 10 jumpers

        Additional Jumper Logic:
            For every 5 additional jumpers beyond the first 10, you get:
            1 extra pizza (free)
            1 extra drink (free)

        Examples:
        -   12 jumpers → 2 pizzas + 2 drinks (purchase separately)
        -   15 jumpers → 2 pizzas + 2 drinks (base) + 1 extra pizza + 1 drink (for 5 extra jumpers)
        -   20 jumpers → 2 pizzas + 2 drinks (base) + 2 extra pizzas + 2 drinks (for 10 extra jumpers)

        *Basic Birthday Party Package:*
        - No food/drinks included - all purchased separately

        *Party Trays:*
        - Always additional purchases for any package

        ---
        
    """
    return prompt


async def get_booking_bot_booking_process_instructions(birthday_party_info,cancel_birthday_party_before_party_date_days,skyzone_food_drinks_info,skip_customer_details_in_prompt,customer_first_name,customer_last_name,customer_email,minimum_deposit_required_for_booking,minimum_jumpers_party,booking_process_instructions):

    check_slots_availability = booking_process_instructions["check_availability_step"]
    collect_child_name_step = booking_process_instructions['collect_child_name_instructions']

    collect_child_name_step = collect_child_name_step.format(
        next_step = """- **Only proceed to *Collect the Date For New Booking Step* after child's name is saved**"""
    )

    collect_date_step = booking_process_instructions['date_collection_step']

    collect_date_step = collect_date_step.format(
        # next_step = """ - **Only proceed to *Collect Time For New Booking Step* after date is confirmed**"""
        next_step_name = """*COLLECT BIRTHDAY PARTY PACKAGE For New Booking*"""
    )
 

    collect_time_of_booking_step = booking_process_instructions['collect_time_of_booking_step']
    collect_time_of_booking_step = collect_time_of_booking_step.format(
        next_step = """ - **Only proceed to *Collect Number of Jumpers For New Booking Step* after party time is saved**""",
        
        next_step_name = """*Collect Number of Jumpers For New Booking Step*"""
    )

    collect_number_of_jumpers_step = booking_process_instructions['collect_number_of_jumpers_instructions']
    collect_number_of_jumpers_step = collect_number_of_jumpers_step.format(
        minimum_jumpers_party = minimum_jumpers_party,
        next_step = """
                - **Only proceed to *Food Drinks and Addons Selection For New Booking* after number of jumpers is saved**
                
        """


    )

    collect_birthday_package_next_step = """Proceed to **Collect the Time For New Booking**"""
    prompt = f"""
    ## *DISCOVERY SCENARIO NEW Booking (Customer doesn't know which package)*

    
    ### *Step 1: Collect Birthday Child's Name For New Booking*
    {collect_child_name_step}
    ----
    ### *Step 2: Collect the Date For New Booking*
    {collect_date_step}
    ----
        
    ### *Step 3: COLLECT BIRTHDAY PARTY PACKAGE For New Booking*
    - Donot Skip *COLLECT BIRTHDAY PARTY PACKAGE For New Booking Step*
    {birthday_party_info['most_popular_birthday_package_prompt']}

    *If YES - Close the Sale:*
    - After user has selected the package, save the selected package using:
    - Use function: save_birthday_party_package_new_booking()
    - Parameters: birthday_party_package_name: [user specified birthday Party package name]
    - {collect_birthday_package_next_step}
    *If NO - Present Other Options:*
    - Continue to *STEP 1.3: Present Other Amazing Options*

   

    *STEP 1.3: Present Other Amazing Options:*
    Only if they ask about other packages Check Availability of Party packages from  Schedule for the Calculated Day from Date
    - Only mention those Birthday Party packages that are available for the calculated day
    "Great question! Based on your date, here are your other options:

    {birthday_party_info['other_birthday_packages_prompt']}

    *When customer asks for details of any specific birthday party package:*
    - Explain the duration breakdown (jump time + party room time or party space time or open air time depending upon the package)
    - Focus on explaining minimum jumpers,Food and drinks included in Package, paper goods, skysocks, Desserts and Cakes Policy, Outside Food Fee(Policy), Birthday Package Perks,additional hour if any,Additional Jumper Cost clearly
    - Reference current birthday party package data for all specifics

    - **If user asks questions or needs clarification during this step:**
    - Answer their question completely and clearly
    - Then IMMEDIATELY return to this step: "Now, back to selecting your package - which package would you like to book for [child's name]'s birthday?"

    After user has selected the package, save the selected package using:
    
    - Use function: save_birthday_party_package_new_booking()
    - Parameters: birthday_party_package_name: [user specified birthday Party package name]
    {collect_birthday_package_next_step}

    ---

      
    ### *Step 4: Collect the Time For New Booking*
    {collect_time_of_booking_step}
    ---
    ###*Step 5: Collect Number of Jumpers For New Booking*
    {collect_number_of_jumpers_step}
    ---    

    

    ###*Step 6: Food Drinks and Addons Selection For New Booking*
        

        
    {skyzone_food_drinks_info['food_drinks_prompt']}
    - After user has completed food drinks and addons selections[if available in selected party package] Proceed to ** Provide User Booking Selection Detail and Cost **
    --- 
        
    ### *Step 7: Provide User Booking Selection Detail and Cost *
    - Donot Skip *Provide User Booking Selection Detail and Cost* Step
    - Must be done *securing the booking*
    MANDATORY: Always provide total cost breakdown - do not wait for user to ask
    *Step 1: Fetch party recap details using function: give_party_recap()
    parameters: None*
    - Present Received party details

    - if user want to change some thing go to those steps and call appropriate  functions mentioned in specific steps

    - If no changes are mentioned by user then proceed to *Securing the Booking Step*
    ---

    ### *Step 8: Securing the Booking*
    "Fantastic! We're going to make [child's name]'s birthday absolutely unforgettable! Let me walk you through how we secure this amazing celebration.

    *Deposit for Securing [child's name]'s booking:*
    - We require a {minimum_deposit_required_for_booking} deposit to hold [child's name]'s party date
    - You'll have 24 hours to complete this deposit
    - This secures everything we've discussed for [child's name]'s special day

    *Our Cancellation Policy* (explained with empathy) [Only Explain Birthday party cancellation policy if user ask for it]:
    - Cancel {cancel_birthday_party_before_party_date_days}+ days before: Full refund to your original payment method
    - Cancel less than {cancel_birthday_party_before_party_date_days} days before: Deposit is non-refundable (we'll have already prepared everything for your party)

    - **If user asks questions or needs clarification during this step:**
    - Answer their question completely and clearly
    - Then IMMEDIATELY return to this step: "Now, Do you want to go ahead with Booking"

    Ask user if he wants to go ahead with final booking:
    - If yes:
      "Move to *Data Collection for New Booking* "
    ---
 
    """
    # step_counter += 1
    
    step_counter =9 
    step_counter += 1
    data_collection_next_step = f"*Step {step_counter}: BOOKING COMPLETION*"
    data_collection_prompt = await collect_customer_details_prompt(skip_customer_details_in_prompt,
                                                                    customer_first_name,customer_last_name,customer_email,data_collection_next_step)
    prompt +=f"""    
        ### *Step 9: Customer Data Collection For New Booking*
    *CRITICAL INSTRUCTIONS Customer Data Collection For New Booking:*

        - ALWAYS use double confirmation (say back + get yes/no)
        - ALWAYS execute this step: IMMEDIATE REPEAT BACK: "I heard  [First name/Last name/Email address]. Is that correct?"
        - ALWAYS spell out names and emails using NATO phonetic alphabet
        - PAUSE between each confirmation step
        - If name sounds wrong, immediately ask to spell it out
        - Always follow email verification step
        - Use SMS fallback for email after first failed attempt
        \n 
        {data_collection_prompt}

        ---
        
        """
    prompt += f"""
    ### {data_collection_next_step}
    - Instruction 
        - Use step {step_counter}.2 only when user did not receive email other wise skip step {step_counter}.2 and proceed to step {step_counter}.3
    Step {step_counter}.1
        - Use function: book_birthday_party_package()
        parameters: 
        None
    
    Step {step_counter}.2
        Example when user did not receive email for payment 
        "I didn't receive the email"
        "I cannot see the email"
        "I haven't received the payment email yet."
        "I didn't get the payment link in my inbox."
        "I'm still waiting for the payment email, but nothing has come through."
        "I checked my inbox and spam folder, but I can't find the payment link."
        "The payment email hasn't arrived; could you please resend it?"

        use function: saved_customer_email()
        - LISTEN for user response
        - If user says "correct", "yes", "right", "that's right" → 
            - Say exactly: "Please check your inbox or spam folder once more"
            
        - If user says "incorrect", "no", "wrong", "that's not right" →
            - Say exactly: "Would you like me to send you a text message where you can reply with your email address?"

            - LISTEN for user response
                - If user agrees to SMS (says "yes", "sure", "okay", "send text") →
                Say exactly: "Great, I'll send a text to your current number. Please reply with your email address. Once you have sent the SMS, let me know. Message and data rates may apply. You can find our privacy policy and terms and conditions at purpledesk.ai."
                Execute function: send_sms_for_email()

            - WAIT for user to say "I have sent you the text message" OR "I replied to your text" OR similar confirmation
                THEN Execute function: check_sms_received_containing_user_email()
                Say: "Thank you! I've received your email address."
                Re-use Step 15.1
    
    Step {step_counter}.3
        "Perfect! [Child's name]'s birthday party is now secured! Here's what happens next:

        *Confirmation Details:*
        - You'll receive a confirmation email within 24 hours with all the party details
        - A reminder will be sent 2 days before [child's name]'s party
        - Your 50% deposit secures the date and time

        Day of Party Reminders:
        - Arrive 15-30 minutes early to get [child's name] ready for their specialcelebration!
        

        Thank you for choosing us for [child's name]'s special celebration! We can't wait to make it unforgettable!"####### Start of Birthday Party Flow #########

    ## *FOOD & DRINK GUIDELINES*

    *Pizza Calculation Logic:*
    - Standard Birthday Party Packages (Epic , Mega VIP, Little Leapers, Glow): 10 jumpers = 2 pizzas + 2 drinks included
    - Additional jumpers: Every 5 jumpers = 1 additional pizza + 1 drink
    - Basic Package: No food/drinks included - all purchased separately

    *Examples:*
    For up to 10 jumpers, the package includes 2 pizzas and 2 drinks. For every extra 5 jumpers after that, you get 1 more pizza and 1 more drink. If the extra jumpers are fewer than 5, food and drinks for them need to be purchased separately.

        10 jumpers → 2 pizzas, 2 drinks included
        11 jumpers → 2 pizzas, 2 drinks included

        15 jumpers → 3 pizzas, 3 drinks included

        17 jumpers → 3 pizzas, 3 drinks included, food/drinks for 2 jumpers bought separately

    *When explaining options:*
    - Mention only first few options from current data
    - Always ask if they want to hear about additional options

    ---
        
    {check_slots_availability}
    
    """
    return prompt

async def construct_birthday_prompt(birthday_party_info,skyzone_food_drinks_info,hours_of_operation_info, location,cancel_birthday_party_before_party_date_days,add_party_reschedule_instruction,party_reschedule_allowed_before_party_date_days,other_items_pricing_info,add_shirts_while_booking,skip_customer_details_in_prompt,
                                   customer_first_name,
                                   customer_last_name,
                                   customer_email,minimum_deposit_required_for_booking,minimum_jumpers_party,edit_booking_instructions,ballon_info,
                                   is_booking_bot,roller_product_ids,current_date,current_day_name,party_booking_allowed_days_before_party_date):
    

                                    
                                    
                                    
    # location="elk grove"
    
    try:
        t_shirts_mapping = {}
        
        if add_shirts_while_booking=="yes":
            add_shirts_instructions = ""
            other_items_pricing_info["item"] = (
                                                    other_items_pricing_info["item"].str.lower()
                                                )
            
            other_items_pricing_info_filtered = other_items_pricing_info[other_items_pricing_info['item']=="t-shirt"]
            if is_booking_bot=="yes":
                roller_product_ids = pd.to_numeric(roller_product_ids, errors="coerce")
                roller_product_ids = pd.Series(roller_product_ids).dropna().astype("Int64")
                other_items_pricing_info_filtered["booking_id"] = (pd.to_numeric(other_items_pricing_info_filtered["booking_id"],
                                                                     errors="coerce")
                                                                    .astype("Int64")
                                                                    )
                other_items_pricing_info_filtered  = other_items_pricing_info_filtered[other_items_pricing_info_filtered["booking_id"].isin(roller_product_ids)]
                

            if not other_items_pricing_info_filtered.empty:
                add_shirts_instructions += f"""### T-Shirts Information Included in some Party Packages 
                if Customer mentions about shirts
                -Step 1: Ask what is the age of your kid and what is the T-shirt size the child can wear?
                - Step 2: When user provides answer of age and size of shirt of child confirm back both to the user
                - Present appropriate shirt from below:
                *Start of Shirts Information:*
                """
                for unique_age_bracket_shirt in other_items_pricing_info_filtered["T-shirt_type"].unique():
                    temp_df = other_items_pricing_info_filtered[other_items_pricing_info_filtered['T-shirt_type']==unique_age_bracket_shirt]
                    for _,row in temp_df.iterrows():
                        add_shirts_instructions += f"""
                        - T-shirt size : {row['T-Shirt_sizes']} | Age Bracket : {row["T-shirt_type"]}
                        """
                        t_shirts_mapping[row['T-Shirt_sizes']]=row["booking_id"]
                
                if is_booking_bot=="yes":

                    add_shirts_instructions += """

                    **Saving T-shirt Process For Booking:**
                    -Ask user: "which T-shirt size will best fit their [child name]?"
                    When user mentions a t-shirt size save it for booking using:
                    Use function: save_t_shirt_size_for_new_booking()
                    Parameters:
                        - t_shirt_size: [user selected T-shirt size]


                    *End of Shirts Information:*"""
                else:
                    add_shirts_instructions += """
                    *End of Shirts Information:*"""

        else:
            add_shirts_instructions = ""
            
        if add_party_reschedule_instruction=="yes":
            rescheduling_policy = f"""
            ** Birthday Party Rescheduling Policy:**

            - Guests get 1 free birthday party reschedule if they notify {party_reschedule_allowed_before_party_date_days}+ days in advance.

            - If the Guest of Honor(The kid who has birthday) is sick, reschedule is usually allowed without a fee.

            - If rescheduling for other reasons (e.g., last-minute change of plans), charge a $200 reschedule fee.

        """
        else:
            rescheduling_policy = ""

        ####end of food and drinks options
        booking_bot_instructions = {}
        if is_booking_bot=="yes":
            collect_birthday_party_package_interest_instructions ="""
            **Critical Birthday Party Package collection check: Search and check through the ENTIRE conversation history for ANY mention of a specific Birthday Party Package earlier**

            - If a specific Party Package is mentioned:
            - Say: "So we're planning [child's name]'s birthday by booking [PACKAGE NAME]?"
            
            - If specific Party Package is not mentioned:
            - Say: "Which Package you want to book to celebrate [child's name]'s birthday?"
            
            - Wait for their response

            - **If user asks questions or needs clarification during this step:**
            - Answer their question completely and clearly
            - Then IMMEDIATELY return to this step: "Now, back to selecting your package - which package would you like to book for [child's name]'s birthday?"

            - **When user confirms or specifies Birthday party package:**
            - Use function: save_birthday_party_package_new_booking()
            - Parameters: birthday_party_package_name: [user specified birthday Party package name]
            {next_step}

            """

            collect_child_name_instructions = """
            - Birthday Child Name is MANDATORY - do not skip this step
            - Say: "Absolutely! I'd be happy to help you book a [PACKAGE NAME]! First, what's the name of the special birthday child we're celebrating?"
            - Wait for their response

            - **If user asks questions or needs clarification during this step:**
            - Answer their question completely and clearly
            - Then IMMEDIATELY return to this step: "Thank you for that question! Now, what's the name of the birthday child we're celebrating?"

            - **When user provides child's name:**
            Use function: save_birthday_child_name_new_booking()
            Parameters: 
                child_name: [birthday child's name]
            {next_step}

            """
            

            date_collection_step = """
            **Critical date collection check: Search and check through the ENTIRE conversation history for ANY mention of a specific day or date earlier**



            **SCENARIO A: If date/day is already mentioned in conversation history:**

            - Acknowledge with confirming question: "So you're planning to celebrate on [day/date], is that correct?"

            - Wait for user confirmation (yes/correct/that's right)

            - After confirmation, use function: identify_day_name_from_date_new_booking()

            Parameters: booking_date: [YYYY-mm-dd format]

            - Then proceed to {next_step_name}



            **SCENARIO B: If date/day is NOT mentioned:**

            - Ask: "When you would  like to book the [PACKAGE NAME]?"

            - OR: "When would you like to celebrate [child's name]'s special day with the [PACKAGE NAME]?"

            - Wait for the response

            - When user provides date, acknowledge: "Perfect! [Day/Date] it is!"

            - Use function: identify_day_name_from_date_new_booking()

            Parameters: booking_date: [YYYY-mm-dd format]

            - Don't proceed to {next_step_name} until the date is confirmed AND function is called



            **WHEN TO SKIP THE INITIAL QUESTION (but still confirm):**

            User says:

            - "Do you have a birthday party package for Saturday?"

            - "What's available this weekend?"

            - "Can I book for tomorrow?"

            - "I want to celebrate on Friday."

            Response: "So you're planning to celebrate on [day they mentioned], correct?" → Wait for confirmation → Call function → Move to {next_step_name}



            **WHEN TO ASK THE QUESTION:**

            User says:

            - "Do you have birthday party packages?"

            - "What birthday party packages are available?"

            - "I'm interested in your birthday packages."

            - "Tell me about the Ultimate package"

            Response: "When you would  like to book the [PACKAGE NAME]?" → Wait for response → Call function → Move to {next_step_name}



            **If user asks questions or needs clarification during this step:**

            - Answer their question completely and clearly

            - Then IMMEDIATELY return to this step: "Now, back to choosing your date - when would you like to celebrate [child's name]'s special day?"



            **CRITICAL: At any point where user specifies a date like "today", "tomorrow", or "on 2025-06-17":**

            Use function: identify_day_name_from_date_new_booking()

            Parameters: booking_date: [YYYY-mm-dd format]



            **Only proceed to {next_step_name} after:**

            1. Date is confirmed by user
            
            
            """
            collect_time_of_booking_step = """
            - Time of Booking collection is MANDATORY - do not skip this step
            - Say: "Perfect choice for [child's name]! What time would work best for the party?"
            - Wait for the user's response

            - **If user asks about availability during this step:**
            - Say: "Great idea! Let me check what times are available for you."
            - Use function: get_available_time_slots()
            - Show available time slots
            - Then IMMEDIATELY return to this step: "Based on availability, what time would work best for [child's name]'s party?"
            - **IMPORTANT: Stay in *Collect the Time For New Booking Step* until user confirms a specific time**

            - **If user asks other questions or needs clarification during this step:**
            - Answer their question completely and clearly
            - Then IMMEDIATELY return to this step: "I understand! Now, what time would work best for [child's name]'s party?"

            - **When user specifies a time for party:**
            Use function: save_birthday_party_time_new_booking()
            Parameters: party_time: [user specified time in 24 Hour Format]
            
            
            {next_step}
            **EXAMPLE FLOW FOR AVAILABILITY CHECK DURING TIME COLLECTION:**

            User: "What times are available?"
            Bot: "Great question! Let me check availability for [child's name]'s [PACKAGE NAME] on [DATE]."
            [Calls - Use function: get_available_time_slots()]
            Bot: "Here are the available time slots: [list available times]. Which time would work best for [child's name]'s party?"
            [STAYS IN *Collect the Time For New Booking Step* - waiting for time selection]

            User: "Is 2 PM available?"
            Bot: [If available] "Yes, 2 PM is available! Perfect choice."
            [Calls save_birthday_party_time_new_booking() with party_time: "14:00"]
            [NOW MOVES TO {next_step_name}]

            """
            

            
            
            collect_number_of_jumpers_instructions = """
                
                - Number of Jumpers collection is MANDATORY - do not skip this step
                - Say: "How many jumpers will be joining [child's name] for this amazing celebration?"
                - Wait for the user's response

                - **If user asks questions or needs clarification during this step:**
                - Answer their question completely and clearly
                - Then IMMEDIATELY return to this step: "Thanks for asking! Now, how many jumpers will be joining [child's name]?"

                - If user is unsure or says "decide later":
                - Use minimum jumpers: {minimum_jumpers_party}
                - Say: "No problem! I'll set it to our minimum of {minimum_jumpers_party} jumpers for now, and you can adjust it later."

                - **When user specifies number of jumpers:**
                Use function: save_number_of_jumpers_new_booking()
                Parameters: number_of_jumpers: [user specified number or minimum_jumpers:{minimum_jumpers_party}]
                {next_step}
                
                """
           
           
            check_availability_step = """
            - When User says check availability of a Birthday Party Package 
            - Use function: get_available_time_slots()
            
            **If room is not available:** "I'm sorry, that time slot isn't available for [child's name]'s party. Let me check what times we have open for [child's name]..." [Present alternative available time slots and get new selection]
            
            """
            
            booking_bot_instructions = {
                "collect_birthday_party_package_interest_instructions": collect_birthday_party_package_interest_instructions,
                "check_availability_step": check_availability_step,
                "collect_time_of_booking_step": collect_time_of_booking_step,
                "collect_number_of_jumpers_instructions": collect_number_of_jumpers_instructions,
                "collect_child_name_instructions": collect_child_name_instructions,
                "date_collection_step": date_collection_step,
            }
            
            booking_process_instructions = await get_booking_bot_booking_process_instructions(birthday_party_info,cancel_birthday_party_before_party_date_days,skyzone_food_drinks_info,skip_customer_details_in_prompt,customer_first_name,customer_last_name,customer_email,minimum_deposit_required_for_booking,minimum_jumpers_party,booking_bot_instructions)

            
        else:
            booking_process_instructions = await get_info_bot_booking_process_instructions(birthday_party_info,cancel_birthday_party_before_party_date_days,skyzone_food_drinks_info,minimum_deposit_required_for_booking)

        direct_booking_scenario_instructions = await provide_direct_booking_scenario(is_booking_bot,booking_bot_instructions,minimum_jumpers_party)
        System_Message = f"""


        ####### Start of Birthday Party Flow #########


        *IMPORTANT GUIDELINES:*
    -Always check schedule availability and location closures in hours of operation for the requested date before recommending party packages
    - Only book birthday parties scheduled at least {party_booking_allowed_days_before_party_date} days from today ({current_date}, {current_day_name}). If the requested date doesn't meet this requirement, proceed to *Short Notice Birthday Party Booking Step*.
    - Only accept birthday party bookings for dates at least {party_booking_allowed_days_before_party_date} days from today date:({current_date},today day: {current_day_name}) as Birthday Party bookings require at least {party_booking_allowed_days_before_party_date} days advance notice. If the requested birthday party booking date is sooner, proceed to *Short Notice Birthday Party Booking Step*.
    - Never mention package prices during explanation (except for additional jumper price). Only mention price of a package if user explicitly asks for it or while booking the package you are allowed to mention all prices.
    - Keep conversations personalized and engaging by using the birthday child's name throughout
    - ALWAYS present the birthday packages, memberships and jump passes detail in conversational language 
    
    
    **Critical Date Collection Procedure for Birthday party packages:**
    MANDATORY STEP: Search through the ENTIRE conversation history for ANY mention of a specific day or date. This includes:
    - User asking "What are your hours for [specific day]?"
    - User mentioning "I want to come on [day]"
    - User asking "Are you open on [day]?"
    - User saying "tomorrow", "today", "this weekend", "any week days" etc.
    - ANY reference to when they want to visit

    If day or date is mentioned in the entire conversation history:
    - If there is mention of date or today or tomorrow, convert date to day name using this function:
      - Use function: identify_day_name_from_date_new_booking()
      -Parameters: booking_date: [YYYY-mm-dd format]
    - Skip any date collection step in birthday party flow

    ---
    ## Short Notice Birthday Party Booking:
   
        Bookings require at least {party_booking_allowed_days_before_party_date} days advance notice. For shorter notice, location confirmation is needed.

        Step 1.0: Inform user: "Our party bookings typically require at least {party_booking_allowed_days_before_party_date} days advance notice. Since your [requested date] falls under short notice, we'll need to confirm availability with our location team."

        Step 1.1: Say exactly: "Regarding your booking request, should I connect you with one of our team members?"

        Step 1.2: If user confirms (yes/similar), call transfer_call_to_agent()
        - transfer_reason: "Short notice booking request for [user requested date]"
    ---

        {rescheduling_policy}
        {edit_booking_instructions}
        {direct_booking_scenario_instructions}
        {booking_process_instructions}


        


        
        
        ### Start of Birthday Party Packages Data:
        {birthday_party_info['birthday_packages_data']}
        **only tell the birthday party package if it is present in Birthday Party Packages Data and is available in hours of operations data**
        Use hours of operations schedule for checking available Birthday party packages for the calculated day:

        ### End of Birthday Party Packages Data
        ---
        {ballon_info}
        ---
        {add_shirts_instructions}
        
        
        

        ####### End of Birthday Party Flow #########


        """
        return System_Message,ballon_info,t_shirts_mapping,add_shirts_instructions
    except BaseException as e:
        print(e)
        import traceback
        traceback.print_exc()


###### memberships prompt
###### memberships prompt
async def  handle_memberships(memberships_info,membership_cancellation_inform_before_days,location):
    
    System_Message = f"""
    
    ### Start Of Memberships Flow ####

    *Direct Question Override*

    - If the user asks a specific membership question, answer it directly and skip the flow.
    
    **- Promotion Retrieval **
        use function: get_promotions_info()
        parameters: 
            user_interested_date = today (mm-dd-yyyy)
            user_interested_event = selected membership
            filter_with = "memberships"

    ## STEP-BY-STEP MEMBERSHIP FLOW:

    {memberships_info['most_popular_membership']}
   
    {memberships_info['other_memberships_highlight']}
    ### STEP 4: Explain Selected Membership
        - Warmly describe:
        - Activity time
        - Features
        - Party discounts (if any)
        - Pricing
        - Parent addon
        - Validity
        - Subscription details

    ## Step 5:Check Promotions (Mandatory)
    - Call get_promotions_info() again using the same parameters before proceeding.

    ### STEP 6: CLOSING & NEXT STEPS
        - Ask: "Would you like to know how to start your membership?"
        - If yes tell user:"Memberships can be  directly subscribed from the Sky Zone mobile app."
        Ask if user wants the link via text.

        If user chooses Share App Link:

        Step 1 (say exactly):
        “Great, I will now send you the link. Message and data rates may apply. You can find our privacy policy and terms and conditions at purpledesk dot ai.”

        Step 1.1:
        “Do I have your permission to send you the link now?”

        If yes → Step 2:

        share_website_app_link(
            links_to_share="Membership subscription Website and App link"
        )


    ## MEMBERSHIP DETAILS TO INCLUDE:
    {memberships_info['memberships_info']}
     
    ## Sky Socks & Neon Shirt Rules
       1. Birthday party → socks included
       2.Membership jump sessions → socks required (or reuse if in good condition)
       3. Glow sessions → socks + Neon T-shirt if required by data

    ## Upselling Strategy:
    - If the user shows interest in the Basic Membership Package, warmly highlight the amazing benefits of the Elite Membership
      
    ## Membership Subscription Process:
    1. subscribed using Sky Zone mobile app
    2. Use share_website_app_link for sending link
    2. Payment: 
       - monthly auto-renew (credit card)
       - Cancellation: {membership_cancellation_inform_before_days} business days notice
    3. Waiver required (valid for 1 year)
    
    ## Membership Cancellation Process:
        If user wants to cancel membership:

        Say: "To help with membership cancellation,Should I transfer you to a team member."
        if user says yes or similar confirmation:
            Call function:

            transfer_call_to_agent(
                transfer_reason="[selected Membership] Cancellation"
            )

    ## Membership Benefits Emphasis:
    - Better value than individual jump passes
    - Flexible use any operating day
    = Access to exclusive member events
    
    *Membership Questions:*
    - Cancel anytime (30-day notice)
    - No long-term commitment
    - Upgrades allowed anytime
    - Valid only at {location.title()}
    - Can freeze for up to 30 days/year
    
    ### End Of Memberships Flow ###
    
    """
    return System_Message   
    

async def  handle_jump_passes(jump_passes_info,location):
    
    
    System_Message = f"""
    
        ### Jump Pass Flow ###

        ## Critical Date Check (Do First, Every Time)
        Search ENTIRE conversation for ANY date/day mention (hours question, "tomorrow", "this weekend", etc.)
        - If found: Convert to day name using "identify_day_name_from_date(date: YYYY-mm-dd)"
        - Always check the date in hours of operation to check location closure before recommending any thing
        - Skip date collection in flow

        ---

        ## Flow Steps

        ### Step 1: Get Jump Date
        **If date already mentioned:** Acknowledge and move to Step 2
        **If not:** "So you're planning to bounce with us for [day/date]?"
        Wait for response.

        ### Step 2: Recommend Pass

        **A. If user requests specific pass by name:**
        - Acknowledge: "I'd be happy to help you book [pass name]!"
        - Confirm date (if not already collected)
        - Skip to Step 4 (booking)

        **B. If discovering needs:**
        1. Present most popular pass first:
        {jump_passes_info['most_popular_pass_prompt']}

        2. If they want more options:
        {jump_passes_info['other_jump_passes_prompt']}

        3. Ask them to select a duration/pass

        4. Provide full details for selected/recommended pass:
        - Duration, Price, Schedule, Sky Socks requirement
        - Glow shirt requirement (if Glow pass)
        - **Call:** `get_promotions_info(user_interested_date: mm-dd-yyyy, user_interested_event: [pass name], filter_with: "jump_pass")`

        **Use:** {jump_passes_info['jump_passes_info']}

        ### Step 3: State Requirements (if not explained)
        **Not included in pass:**
        - Sky Zone waiver (valid 1 year)
        - Sky Socks (purchase or reuse if good condition)
        - Neon T-shirt (Glow Events only, if required per data)

        "Jump sessions require these items."

        ### Step 4: Close Sale

        "Would you like to purchase [selected pass]?"

        **If YES:**
        "Jump passes can be booked on call or via Sky Zone mobile app. Would you prefer to book now on call or receive the app link via text?"

        **If "Book Now or similar statement":**
        1. Ask consent:"Regarding [specific jump pass booking] Should I connect with one of our team members?"
            - if user says yes or similar consent:
                 **Call:** `transfer_call_to_agent(transfer_reason: "[pass + quantity/ages if mentioned] Reservation, Date: [date]")`

        **If "Share Link":**
        1. "I'll send the link. Message and data rates may apply. Privacy policy at purpledesk dot ai."
        2. "Do I have your permission to send the link?"
        3. If yes: **Call:** `share_website_app_link(links_to_share: "Jump pass website and app link")`

        ---
        ## Execution Notes
        - Use natural punctuation, pauses, commas
        - Wait for responses between steps

    """
    
    return System_Message    




async def make_master_prompt(initial_greeting,birthday_party_packages_prompt,memberships_prompt,jump_passes_prompt,personality_traits,caller_number,current_date,current_time, discount_info,hours_of_operation_info, policies_info, faqs_info, terminology_info,current_day_name,other_items_pricing_info,location, address, formatted_promotional_data,group_rates_info,rental_facility_info):
    
    location = location.lower()
    
    system_prompt = f""""
    {personality_traits}

    ## Call Context
    - *Customer's Phone Number*: {caller_number}
    - *Today Date*: {current_date}
    - *Current Time (Today)*: {current_time}
    - *Today Day Name*:{current_day_name}

    {birthday_party_packages_prompt}
    {memberships_prompt}
    {jump_passes_prompt}
    {group_rates_info}
    {rental_facility_info}
    
    ### Start Of Lost Items Flow ####
    ## Lost Item Details Collection Procedure:
        *Ask step-by-step question*
        1. Ask full name of customer
        [Customer provides their Full Name]
        2. Ask Lost item name
        [Customer provides Lost Item Name]
        3. Ask description of lost item
        [Customer provides description of Lost Item]
        4. Ask visiting date when he lost his item
        [Customer provides the date of visit]
        5. Ask user to use this phone number: {caller_number} to contact back or he wants to provide an alternate phone number[must be 10 digits] to contact him back
        [Customer provides his personal 10 digits phone number]
        - you have access to save_lost_items function which will save the lost item details 
            Function details:
                - Name: save_lost_items
                - Parameters:
                    1.full_name 
                    2.lost_item_name 
                    3.description_of_lost_item
                    4.visiting_date
                    5.phone_number

    ### End Of Lost Items Flow ####
    
    
    

---

    ### Hours of Operation Inquiry Process

    **Current Context:** {current_date}, {current_day_name}, {current_time}

    #### Step 1: Identify Day
    - Ask: "What day are you hoping to bounce with us?" (if not mentioned)
    - For dates mentioned, convert to day name using `identify_day_name_from_date(YYYY-mm-dd)`

    #### Step 2: Check Closures FIRST
    - **For TODAY:** Check if {current_date} is closed
    - **For FUTURE:** Calculate actual date from {current_date}, then check closures
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

    **Schedule Reference:** {hours_of_operation_info}
    **Discounts:** {discount_info}

    **Critical Rules:**
    - ALWAYS check closures first for the specific calculated date
    - CALCULATE actual dates for future day requests from {current_date}
    - Special hours override regular hours completely
    - Never mention unavailable programs
    - Always ask about visit purpose

    ### End of Hours of Operation Inquiry Process ###
    
    
    ## Location

    ### Step 1: Primary Location Response
        - When a user asks about Sky Zone {location.replace("_"," ").upper()}'s location, provide this information:
        - **Address**: Sky Zone {location.replace("_"," ").upper()} is located at {address}
        - If directions are requested, **Say Exactly**: "you can use google map to find skyzone {location.replace("_"," ").upper()}"

    ### Step 2: Follow-up Direction Requests
        Step: 2.1:
            Say exactly: "To help your query on the direction I will connect you to our team member."
        Step: 2.2:
            *Use function: transfer_call_to_agent()*
                - transfer_reason: "The user is requesting directions to the location."

    ### Step 3: Visit Planning Inquiry
        - **After providing location information, if the customer has not previously mentioned a specific visiting day or date**:
        - **Ask exactly**: "Are you planning to visit us today or another day?"

    ##  Important Execution Notes:
        - Only proceed to the agent connection response if the user persists with direction questions after the initial location and google maps guidance
        - The visit planning question should only be asked once per conversation and only if no specific date/date was mentioned earlier
        - Use the exact phrases provided for consistency
        
    ## Other Items Pricing Information

    {other_items_pricing_info}

    {formatted_promotional_data}

    
    
    ## Frequently Asked Questions (FAQs)
    {faqs_info.replace(".","")}
   
   
   ### Policies 
   {policies_info}

   ##Skyzone Terminology
   {terminology_info}

   ## Reminders for Effective Calls
    - Always ask **one question at a time**
    - Use the child's name throughout the calls
    - Never fake function calls — use real ones

---

   
    """
    return system_prompt


async def load_sheet(session, sheet_id, name):
    # print(name)
    """Optimized sheet loading with aiohttp and better error handling"""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={name}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                # print("data loaded!!")

                # Use StringIO to avoid file I/O
                from io import StringIO
                df = pd.read_csv(StringIO(content))
                # if name == "Promotions":
                #     print(df, name)
                return name, df
            else:
                print(f"HTTP {response.status} for sheet '{name}'")
                return name, None
    except Exception as e:
        print(f"Failed to load sheet '{name}': {e}")
        return name, None

def process_dataframe_sync(df, location):
    """Synchronous dataframe processing - optimized"""
    if df is None:
        return None
    
    # More efficient string operations
    if location is not None and "Location" in df.columns:
        # Filter first, then process
        df = df[df["Location"].str.lower() == location.lower()].copy()
    
    # Vectorized string operations
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].astype(str).str.lower()
    
    return df

async def clean_prompt_keep_newlines(text: str) -> str:
    # Remove extra spaces/tabs inside lines
    text = re.sub(r'[ \t]+', ' ', text)

    # Remove extra blank lines (keep only one)
    text = re.sub(r'\n\s*\n+', '\n', text)

    # Strip spaces at the start/end of each line
    lines = [line.strip() for line in text.splitlines()]
    
    return "\n".join(lines)

def parse_single_sheet(xls: pd.ExcelFile, sheet_name: str):
    """Parse a single sheet from ExcelFile."""
    try:
        if sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)
            return sheet_name, df
        else:
            return sheet_name, None
    except Exception as e:
        print(f"❌ Failed to parse '{sheet_name}': {e}")
        return sheet_name, None
async def load_sheets_concurrently(file_path: str, sheet_names: list[str]) -> dict:
    """Load multiple sheets in parallel using asyncio.gather + asyncio.to_thread."""
    sheet_dfs = {}
    xls = pd.ExcelFile(file_path)

    # Run all sheet parsing concurrently using asyncio.to_thread
    tasks = [
        asyncio.to_thread(parse_single_sheet, xls, name)
        for name in sheet_names
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            print(f"⚠️ Exception: {result}")
            continue
        name, df = result
        # if df is not None and not df.empty:
        #     sheet_dfs[name] = df
        if df is not None:
            sheet_dfs[name] = df

    print(f"✅ Loaded sheets: {list(sheet_dfs.keys())}")
    return sheet_dfs

minimum_jumpers_party = None
add_additional_hour_of_jump_instruction = None
party_booking_allowed_days_before_party_date = None
party_reschedule_allowed_before_party_date_days = None
cancel_birthday_party_before_party_date_days = None
add_shirts_while_booking = None
elite_member_skysocks_price = None
elite_member_party_discount_percentage = None
membership_cancellation_inform_before_days = None
timezone = None
location_name = None
address = None
address_map_link = None
twilio_number = None
transfer_number = None
from_email_address = None
guest_of_honor_included_in_minimum_jumpers_party = None
add_party_reschedule_instruction = None



###new booking variables
is_booking_bot = None
pitch_ballons_while_booking = None
is_edit_bot = None
minimum_deposit_required_for_booking = None
add_additional_half_hour_of_jump_instruction = None
pitch_group_rates = None
additional_jumper_discount = None
pitch_rental_facility = None
add_party_space_sentence = None

### where to add party inclusion
add_inclusions_in = None

async def load_data(caller_number,sheet_id,skip_customer_details_in_prompt,customer_first_name,customer_last_name,customer_email,is_edit_details,edit_booking_details_tuple,roller_product_ids):
    global minimum_jumpers_party,add_additional_hour_of_jump_instruction,party_booking_allowed_days_before_party_date, party_reschedule_allowed_before_party_date_days,add_shirts_while_booking
    global elite_member_skysocks_price,elite_member_party_discount_percentage, membership_cancellation_inform_before_days, timezone ,location_name ,address ,address_map_link 
    global twilio_number ,transfer_number ,from_email_address,guest_of_honor_included_in_minimum_jumpers_party,cancel_birthday_party_before_party_date_days,add_party_reschedule_instruction 
    global is_booking_bot,pitch_ballons_while_booking,is_edit_bot,minimum_deposit_required_for_booking,add_additional_half_hour_of_jump_instruction,pitch_group_rates,additional_jumper_discount,pitch_rental_facility,add_party_space_sentence,add_inclusions_in
    initial_greeting = ""
    personality_traits = """
            ## AUDIO CLARITY CHECK:

                -If audio is unclear, noisy, or unintelligible, respond:
                    "I'm sorry, I didn't catch that clearly. Could you please repeat your question?"
                - Do not guess, assume, or explain services until the request is clear.
                - Always ask for clarification and wait for a clear response.
            ---
            ##TOPIC IDENTIFICATION:
            Before explaining any service, you MUST:

            1. IDENTIFY the specific topic the user is asking about:
            - Jump Passes (day passes, pricing, hours, etc.)
            - Birthday Party Packages (party options, booking, pricing, etc.)
            - Memberships (monthly plans, benefits, etc.)
            - General FAQs (safety, rules, location, etc.)
            - Irrelevant topics (Employement, Shipment, Delivery, Job application, payroll information etc)

            2. If unsure, confirm:
                "Just to clarify, are you asking about [TOPIC]?"

            3. STAY IN THE CORRECT FLOW:
            -Discuss only the selected topic
            - Don't mix topics unless the user requests it

            FLOW SWITCHING PROTOCOL:
            -If the user changes topics:
                "I see you're now asking about [NEW TOPIC]. Let me help you with that."
            -Drop the previous context and switch.
            -If they seem unsure, ask:
                "Do you need info about jump passes, birthday party packages, or memberships?"    
           --- 
            
            ## Phone Conversation Guidelines
            -Respond in English only
            - Ask one question at a time
            - Speak clearly at a moderate pace
            - Use simple, conversational language
            - Allow pauses and repeat key details for confirmation
            - Summarize occasionally to stay on track
            - Use proper punctuation and natural pauses in every sentence.Use commas to indicate pauses where someone would naturally take a breath.

            ## Voice & Personality
            - *Tone and Personality*: use emotions like empathy,warmth and calmness
            - *Pitch*: calm and conversational

            ## Opening Line & Bot Question Handling
            - If asked "Are you a bot?" or "Are you human?", say: *"I'm here to help you with jump passes,membership options or plan an amazing birthday party! How can I assist you?"*
           
            ### Number, Digit, Time and website Formatting Guidelines
            
            Instruction: All numbers and digits must be written out in full English words rather than using numeric symbols.
            Formatting Rules:

            - Convert all numeric characters to their spoken English equivalents
            - Maintain natural speech patterns and clarity
            - Include currency denominations when applicable

            - Examples:
                - Pricing Format:
                    Input: $29.99
                    Output: "twenty nine dollars and ninety nine cents"

                - Phone Number Format:
                    Input: 1 5 0 8 6 3 4 2 9 7
                    Output: "One Five zero eight six three four two nine seven"

                - Time format:
                    Input: 8 p.m
                    Output: "8 PM"
                    Input: 10 a.m
                    Output: "10 AM"

                - Jump and Party Time Formate:
                    Input: 120 minutes
                    Output: "One hundred twenty minutes"
                    Input: 90 minutes
                    Output: "Ninety minutes"

                - website : "skyzone dot com slash trumbull"(instead of skyzone.com/trumbull)
            ---    
            ### Out-of-Scope Query Handling
                When you encounter any of the following situations, use this standardized process
                    
                **Step 1:** Say "Regarding [user query about topic], should I connect you to one of our team members?"

                **Step 2:** If user confirms (yes/sure/okay/please/etc.)
                   - use function: transfer_call_to_agent()
                   - Parameter: transfer_reason - "[description of the user's request that requires human assistance]"

                **Situations requiring transfer:**

                1. **Employee Issues** - Attendance, shifts, illness, lateness
                Transfer reason: "Employee attendance issue - [brief description]"

                2. **Delivery/Shipment** - Package pickup, deliveries, closed location
                Transfer reason: "Delivery/shipment inquiry - [brief description]"

                3. **Return Calls/Follow-ups** - Previous conversations, call disconnections, follow-up requests
                Transfer reason: "Returning call - [brief description]"

                4. **Missing Confirmations** - Party bookings, memberships, jump passes without confirmation emails/receipts
                Transfer reason: "Missing confirmation - [specify: party/membership/jump pass]"

                5. **Cancellations/Refunds** - Membership cancellation, freeze, refund requests for any service
                Transfer reason: "Cancellation/refund request - [specify service and request]"

                6. **Booking Changes** - Reschedule, time changes, postpone, e-vite issues
                Transfer reason: "Booking modification - [specify change needed]"

                7. **Complaints** - Any complaint or complaint status check
                Transfer reason: "Complaint - [description of issue]"

                8. **Unknown Queries** - Questions outside your knowledge base
                Transfer reason: "[specific user query]"
        ---
        

        ## Case: User requests to speak with human support
        When a user explicitly asks to speak with a human/agent/manager/supervisor/front desk/customer service/representative, always call the 'received_transfer_request_from_user' function with parameter 'user_query = "customer wants to speak to an agent or the any user query "'.

        Note: The 'received_transfer_request_from_user' function is distinct from 'transfer_call_to_agent', which is reserved exclusively for membership cancellations, Jump pass bookings, Birthday Party bookings, or modifications to existing party bookings.
        ---

    """
    try:
    
        # Manually specify all sheet/tab names exactly as they appear
        sheet_names = ["prompt_variables","party_packages", "food_drinks", "jump_passes",
                    "hours_of_operation","item_prices","memberships",
                    "discounts","policies","faqs","teminology", "Promotions",
                    "party_inclusions_addon_category","party_balloon","Group_booking","Rental_facility"]
        
        
        file_path = await download_google_sheet(sheet_id)
        # print(file_path)
        sheet_dfs = await load_sheets_concurrently(file_path, sheet_names)
        
        
        

    # Assign values from sheet to variables (must have columns: "variable_name", "value")
        for _, row in sheet_dfs['prompt_variables'].iterrows():
            var_name = row["variable_name"]
            var_value = row["value"]
            # print(var_name)
            # assign to variable if it exists in globals
            # print(globals())
            if var_name in globals():
                globals()[var_name] = var_value

        
        print(f"is_booking_bot:{is_booking_bot}")
        ## adjusting timezone according to timezone mentioned
        california_time = datetime.now(ZoneInfo(timezone))
        
        # Separate date and time
        current_date = california_time.date()
        current_time = california_time.strftime("%I:%M %p")
        current_day_name = california_time.strftime("%A")
        human_understandable_date = california_time.strftime("%d %B, %Y")
        current_date = f"{current_date} ( {human_understandable_date} )"

        
        ### end of adjusting timezone according to timezone mentioned

        ### end of getting prompt variables from sheet
        
        # Phase 2: Process dataframes concurrently
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=4) as executor:
            df_processing_tasks = {
                name: loop.run_in_executor(
                    executor, 
                    process_dataframe_sync, 
                    sheet_dfs.get(name), 
                    location_name if name not in ['faqs', 'teminology', 'policies'] else None
                )
                for name in ['party_packages', 'food_drinks', 'hours_of_operation', 'jump_passes', 
                            'item_prices', 'memberships', 'discounts', 'faqs',
                            'teminology', 'policies', 'Promotions',"party_inclusions_addon_category","party_balloon","Group_booking","Rental_facility"]
            }
            
            processed_results = await asyncio.gather(*df_processing_tasks.values(), return_exceptions=True)

        # Create processed dataframes dictionary
            processed_dict = {}
            for name, result in zip(df_processing_tasks.keys(), processed_results):
                if isinstance(result, Exception):
                    print(f"⚠️ Exception processing sheet '{name}': {result}")
                elif result is not None:
                    processed_dict[name] = result
                else:
                    print(f"⚠️ Sheet '{name}' returned None")
        # Process all dataframes concurrently
        loop = asyncio.get_event_loop()

        

        
        hours_task = asyncio.create_task(
            process_comprehensive_schedule(processed_dict['hours_of_operation'],timezone)
        )
        
        # Phase 4: Start other processing tasks that don't depend on hours
        independent_tasks = await asyncio.gather(
            extract_items_info(processed_dict['item_prices'],add_shirts_while_booking),
            extract_discount_info(processed_dict['discounts']),
            extract_faqs_for_llm(processed_dict['faqs']),
            extract_terminology_info(processed_dict['teminology']),
            extract_policies_llm_friendly(processed_dict['policies']),
            process_birthday_food(processed_dict['party_packages'], processed_dict['food_drinks'],processed_dict['hours_of_operation'],
                                guest_of_honor_included_in_minimum_jumpers_party,
                                minimum_jumpers_party,add_additional_hour_of_jump_instruction,
                                add_additional_half_hour_of_jump_instruction,
                                is_booking_bot,processed_dict["party_inclusions_addon_category"],is_edit_bot,is_edit_details,
                                    edit_booking_details_tuple,pitch_ballons_while_booking,additional_jumper_discount,roller_product_ids),
            process_promotions(processed_dict['Promotions']),
            extract_balloons_info(processed_dict['party_balloon'],pitch_ballons_while_booking,is_booking_bot),
            extract_group_bookings(processed_dict['Group_booking'],pitch_group_rates),
            extract_rental_facility_bookings(processed_dict['Rental_facility'],pitch_rental_facility),
            return_exceptions=True
        )
        for idx, task in enumerate(independent_tasks):
            if isinstance(task, Exception):
                print(f"⚠️ Task {idx} raised an exception: {repr(task)}")
                print("---- TRACEBACK ----")
                traceback.print_exception(type(task), task, task.__traceback__)
                print("-------------------\n")

        # Wait for hours processing to complete
        scheduled_jump_types_dict = await hours_task
        # print(scheduled_jump_types_dict)
        # print(scheduled_jump_types_dict)
        print(scheduled_jump_types_dict)
        hours_of_operation_info = await format_schedule_for_display(scheduled_jump_types_dict)
        # print(hours_of_operation_info)
        # print('-------------------------------------')
        # print(hours_of_operation_info)
        # print('-------------------------------------')

        
        # Phase 5: Process tasks that depend on hours
        dependent_tasks = await asyncio.gather(
            jump_pass_info(processed_dict['jump_passes'], scheduled_jump_types_dict,processed_dict['hours_of_operation']),
            extract_membership_info(processed_dict['memberships'], scheduled_jump_types_dict),
            return_exceptions=True
        )
        
        # Unpack all results
        (other_items_pricing_info, discount_info, faqs_info, terminology_info, 
        policies_info, birthday_food_result, promotions_dict,balloons_info,group_rates_info,rental_facility_info) = independent_tasks
        # print(promotions_dict)

        
        jump_passes_info, memberships_info = dependent_tasks
        birthday_party_info, skyzone_food_drinks_info = birthday_food_result
        birthday_mappings = birthday_party_info["birthday_mappings"]
        birthday_packages_data = birthday_party_info["birthday_packages_data"]
        inclusions_addons_mapping = skyzone_food_drinks_info["inclusions_addons_mapping"]
        reverse_mapping_roller_products = skyzone_food_drinks_info["reverse_mapping_roller_products"]
        edit_food_prompt = skyzone_food_drinks_info["edit_food_prompt"]
        existing_booking_details = skyzone_food_drinks_info["existing_booking_details"]
        max_step_counter_edit = skyzone_food_drinks_info["max_step_counter_edit"]

        edit_booking_instructions = await provide_editing_instructions(is_edit_bot,existing_booking_details,edit_food_prompt,max_step_counter_edit,minimum_jumpers_party,birthday_mappings,birthday_packages_data)


        ######### Transforming Bot into booking bot
        
        ######### End of Transforming Bot into Booking Bot
        
        # Phase 6: Generate final prompts concurrently
        prompt_tasks = await asyncio.gather(
            construct_birthday_prompt(birthday_party_info, skyzone_food_drinks_info, hours_of_operation_info,
                                    location_name,cancel_birthday_party_before_party_date_days,
                                    add_party_reschedule_instruction,
                                    party_reschedule_allowed_before_party_date_days,
                                    processed_dict['item_prices'],
                                    add_shirts_while_booking,
                                    skip_customer_details_in_prompt,
                                    customer_first_name,
                                    customer_last_name,
                                    customer_email,
                                    minimum_deposit_required_for_booking,
                                    minimum_jumpers_party,
                                    edit_booking_instructions,
                                    balloons_info,
                                    is_booking_bot,
                                    roller_product_ids,
                                    current_date,
                                    current_day_name,
                                    party_booking_allowed_days_before_party_date,
                                    
                                    ),
            handle_memberships(memberships_info,membership_cancellation_inform_before_days, location=location_name),
            handle_jump_passes(jump_passes_info, location=location_name),
            format_promotions_dict(promotions_dict),
            return_exceptions=True
        )
        
        birthday_party_packages_data, memberships_prompt, jump_passes_prompt, formatted_promotions_data = prompt_tasks
        
        birthday_party_packages_prompt,ballon_info,t_shirts_mapping,add_shirts_instructions = birthday_party_packages_data
        
        # # Generate master prompt
        master_prompt = await make_master_prompt(
            initial_greeting, birthday_party_packages_prompt, memberships_prompt, 
            jump_passes_prompt, personality_traits, caller_number, current_date, 
            current_time, discount_info, hours_of_operation_info, policies_info, 
            faqs_info, terminology_info, current_day_name,other_items_pricing_info, location_name, address, formatted_promotions_data,group_rates_info,rental_facility_info
        )

        master_prompt = await clean_prompt_keep_newlines(master_prompt)

        
        with open("zmaster_prompt.md", "w", encoding="utf-8") as file:
            file.write(master_prompt)
            print('wrote to file')
        
        global _http_session
        if _http_session and not _http_session.closed:
            await _http_session.close()
        try:
            gc.collect()
            await asyncio.sleep(0.2)  # brief delay so file handles close
            if os.path.exists(file_path):
                os.remove(file_path)
                # print(f"Deleted temp file: {file_path}")
        except PermissionError:
            print(f"Retrying delete for {file_path}...")
            try:
                await asyncio.sleep(0.5)
                os.remove(file_path)
            except Exception as e:
                print(f"Still failed to delete {file_path}: {e}")
        except Exception as e:
            print(f"Failed to delete temp file {file_path}: {e}")
        prompt_variables = {
        "minimum_jumpers_party": minimum_jumpers_party,
        "guest_of_honor_included_in_minimum_jumpers_party": guest_of_honor_included_in_minimum_jumpers_party,
        "add_additional_hour_of_jump_instruction": add_additional_hour_of_jump_instruction,
        "party_booking_allowed_days_before_party_date": party_booking_allowed_days_before_party_date,
        "cancel_birthday_party_before_party_date_days": cancel_birthday_party_before_party_date_days,
        "add_party_reschedule_instruction": add_party_reschedule_instruction,
        "party_reschedule_allowed_before_party_date_days": party_reschedule_allowed_before_party_date_days,
        "add_shirts_while_booking": add_shirts_while_booking,
        "elite_member_skysocks_price": elite_member_skysocks_price,
        "elite_member_party_discount_percentage": elite_member_party_discount_percentage,
        "membership_cancellation_inform_before_days": membership_cancellation_inform_before_days,
        "timezone": timezone,
        "location_name": location_name,
        "address": address,
        "address_map_link": address_map_link,
        "twilio_number": twilio_number,
        "transfer_number": transfer_number,
        "from_email_address": from_email_address,
        "pitch_ballons_while_booking":pitch_ballons_while_booking,
        "balloon_prompt":ballon_info,
        "t_shirts_mapping":t_shirts_mapping,
        "add_shirts_instructions":add_shirts_instructions,
        "birthday_mappings":birthday_mappings,
        "inclusions_addons_mapping":inclusions_addons_mapping,
        "reverse_mapping_roller_products":reverse_mapping_roller_products,
        "add_inclusions_in":str(add_inclusions_in).lower()


        }

        return master_prompt, promotions_dict ,prompt_variables, current_date,current_time

    # asyncio.run(save_prompts_files())
    except Exception as e:
        
        print(traceback.print_exc())
        print(e)
