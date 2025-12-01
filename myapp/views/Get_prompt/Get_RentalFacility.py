
import asyncio
import pandas as pd
from datetime import datetime, timedelta, date
from typing import List, Tuple, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import pytz

from asgiref.sync import sync_to_async
from myapp.model.rental_facility_model import RentalFacility


async def get_rental_facility_info(location_id: int, rental_facility_flag: str) -> dict:
    """
    Get rental facility information from database with structured data
    
    Args:
        location_id: The location ID to fetch rental facilities for
        rental_facility_flag: Flag indicating if rental facility is available ('yes' or 'no')
    
    Returns:
        Dictionary with formatted prompt and structured data
    """
    # Helper function to check if a value is valid
    def is_valid(value):
        if value is None:
            return False
        if isinstance(value, (str, int, float)):
            if isinstance(value, str):
                return value.strip() not in ["", "nan", "NaN", "None", "null"]
            return True
        return False
    
    rental_facility_prompt = ""
    structured_data = {
        "location_id": location_id,
        "rental_facility_flag": rental_facility_flag,
        "total_packages": 0,
        "packages_by_group": {},
        "available": False
    }
    
    if rental_facility_flag.lower() == 'yes':
        # Fetch rental facilities from database for the given location
        rental_facilities = await sync_to_async(list)(
            RentalFacility.objects.filter(location_id=location_id).order_by('rental_group_name')
        )
        
        structured_data["available"] = True
        structured_data["total_packages"] = len(rental_facilities)
        
        # Convert to DataFrame to maintain compatibility with existing processing logic
        rental_data = []
        for rental_obj in rental_facilities:
            rental_data.append({
                'rental_group_name': rental_obj.rental_group_name or "",
                'Rental_jumper_group': rental_obj.rental_jumper_group,
                'inclusions': rental_obj.inclusions or "",
                'per_jumper_price': float(rental_obj.per_jumper_price) if rental_obj.per_jumper_price else 0.0,
                'Minimum_jumpers': rental_obj.minimum_jumpers,
                'maximum_jumpers': rental_obj.maximum_jumpers,
            })
            
            # Add to structured data
            group_name = rental_obj.rental_group_name or "Uncategorized"
            if group_name not in structured_data["packages_by_group"]:
                structured_data["packages_by_group"][group_name] = []
            
            structured_data["packages_by_group"][group_name].append({
                "rental_jumper_group": rental_obj.rental_jumper_group,
                "per_jumper_price": float(rental_obj.per_jumper_price) if rental_obj.per_jumper_price else 0.0,
                "minimum_jumpers": rental_obj.minimum_jumpers,
                "maximum_jumpers": rental_obj.maximum_jumpers,
                "inclusions": rental_obj.inclusions or "",
                "rental_facility_id": rental_obj.rental_facility_id
            })
        
        # Create DataFrame
        df_rental_facility = pd.DataFrame(rental_data)
        
        rental_facility_transfer_step = "*Rental Facility Group Booking Transfer Procedure Step*"
        rental_facility_prompt = f"""### Start of Rental Facility Group Booking Flow ###\n
        - For Group Booking Rental Facility Packages are provided
        - Rental Facility group booking packages can be booked during normal business hours only. 
        - Donot mention any prices of rental packages and in case of any confusion go to {rental_facility_transfer_step}
        """

        rental_facility_data = """"""
        
        if not df_rental_facility.empty:
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
        else:
            rental_facility_data = "No rental facility packages available for this location."

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
    
    return {
        "formatted_prompt": rental_facility_prompt,
        "structured_data": structured_data
    }