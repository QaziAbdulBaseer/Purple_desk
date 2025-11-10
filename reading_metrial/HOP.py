import asyncio


async def get_california_time(timezone):
    """Get current California time"""
    california_tz = pytz.timezone(timezone)
    return datetime.now(california_tz)

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object (timezone-naive)"""
    if not date_str or date_str == "nan" or date_str == "":
        return None
    try:
        return datetime.strptime(date_str, "%B %d,%Y")
    except:
        try:
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
    """Convert time string (e.g., '11 AM', '12 PM') to minutes since midnight"""
    if not time_str:
        return 0
    
    time_str = str(time_str).strip().upper()
    
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
                    return result
            elif start_date and start_date.date() == target_date_naive.date():
                result["status"] = "closed"
                reason = row.get("reason", "Operational reasons")
                result["notes"].append(f"Location closed on {target_date_str} - {reason}")
                result["events"] = {}
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

def is_date_in_seven_day_range(date_to_check: datetime, start_date: datetime) -> bool:
    """Check if a date falls within the 7-day range starting from start_date"""
    if not date_to_check:
        return False
    
    # Convert to naive datetime for comparison
    if hasattr(start_date, 'tzinfo') and start_date.tzinfo is not None:
        start_date_naive = start_date.replace(tzinfo=None)
    else:
        start_date_naive = start_date
        
    if hasattr(date_to_check, 'tzinfo') and date_to_check.tzinfo is not None:
        date_to_check_naive = date_to_check.replace(tzinfo=None)
    else:
        date_to_check_naive = date_to_check
    
    end_date = start_date_naive + timedelta(days=6)
    return start_date_naive.date() <= date_to_check_naive.date() <= end_date.date()

async def get_future_special_events_async(df: pd.DataFrame, start_date: datetime) -> List[Dict]:
    """Get future special hours events (excluding those in the 7-day range) - async version"""
    def _process_special_events():
        special_events = []
        special_hours = df[df["hours_type"] == "special"]
        
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
                    jump_type = row["jump_type"].replace('_', ' ').title() if row["jump_type"] else ""
                    
                    event_info = {
                        "jump_type": jump_type,
                        "start_date": start_date_obj.strftime("%A, %B %d, %Y"),
                        "time": time_range,
                        "ages": row["ages_allowed"]
                    }
                    
                    if end_date_obj and end_date_obj != start_date_obj:
                        event_info["end_date"] = end_date_obj.strftime("%A, %B %d, %Y")
                    
                    special_events.append(event_info)
        
        return sorted(special_events, key=lambda x: parse_date(x["start_date"].split(", ", 1)[1]))
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _process_special_events)

async def get_future_closures_async(df: pd.DataFrame, start_date: datetime) -> List[Dict]:
    """Get future closure dates (excluding those in the 7-day range) - async version"""
    def _process_closures():
        closures = []
        closed_entries = df[df["hours_type"] == "closed"]
        
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
        
        return sorted(closures, key=lambda x: parse_date(x["start_date"].split(", ", 1)[1]))
    
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
                        "time": row["end_time"],
                        "reason": row.get("reason", "Operational reasons")
                    })
        
        return sorted(early_closings, key=lambda x: parse_date(x["date"].split(", ", 1)[1]))
    
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
                        "time": row["start_time"],
                        "reason": row.get("reason", "Operational reasons")
                    })
        
        return sorted(late_openings, key=lambda x: parse_date(x["date"].split(", ", 1)[1]))
    
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
            jump_types = [jt for jt in jump_types if jt and jt != "" and jt != "nan"]
            
            for jump_type in jump_types:

                jump_df = regular_hours[regular_hours["jump_type"] == jump_type]
                # jump_type_available_birthday_packages_df = birthday_party_df[birthday_party_df["jump_type"] == jump_type]
                # jump_type_available_jump_passes_packages_df = jump_pass_df[jump_pass_df["jump_type"] == jump_type]
                
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
    

async def process_comprehensive_schedule(hours_df: pd.DataFrame,timezone:str) -> Dict:
    """
    Process the hours dataframe to create comprehensive schedule information - optimized async version
    """
    # Clean the dataframe
    

    hours_df = hours_df.astype(str).apply(lambda x: x.str.strip())
    hours_df.replace(["nan", ""], "", inplace=True)
    
    # ADD BACK THE PROPER TIME PARSING
    hours_df['start_time'] = pd.to_datetime(hours_df['start_time'], format='%H:%M:%S', errors='coerce').dt.strftime('%I:%M %p')
    hours_df['end_time'] = pd.to_datetime(hours_df['end_time'], format='%H:%M:%S', errors='coerce').dt.strftime('%I:%M %p')
    
    # Now remove the :00 from formatted times
    hours_df['start_time'] = hours_df['start_time'].str.replace(r':00(?=\s[AP]M)', '', regex=True)
    hours_df['end_time'] = hours_df['end_time'].str.replace(r':00(?=\s[AP]M)', '', regex=True)
    # print(hours_df['start_time'], hours_df["end_time"])
    # After time formatting, add:
    
    # Filter rows by jump_type
    


    # print(to_keep)
    
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
    # print(schedule_result)
    return schedule_result


async def format_schedule_for_display(schedule_data: Dict) -> str:
    """Format the schedule data for easy reading - async version"""
    def _format_output():
        output_lines = []
        
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
            # print(schedule_data["seven_day_schedule"])
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
        
        return "\n".join(output_lines)
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _format_output)




hours_task = asyncio.create_task(
        process_comprehensive_schedule(processed_dict['hours_of_operation'],timezone)
    )



scheduled_jump_types_dict = await hours_task

hours_of_operation_info = await format_schedule_for_display(scheduled_jump_types_dict)
