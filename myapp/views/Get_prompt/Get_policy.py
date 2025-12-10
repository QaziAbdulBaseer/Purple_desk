



import asyncio
import pandas as pd
from datetime import datetime, timedelta, date
from typing import List, Tuple, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import pytz

from asgiref.sync import sync_to_async
from myapp.model.policy_model import Policy
# Add this import
from myapp.model.locations_model import Location


async def get_policies_for_llm(location_id: int) -> dict:
    """
    Main function to get formatted policy information from database
    
    Args:
        location_id: The location ID to fetch policies for
    
    Returns:
        Dictionary with formatted policy string and structured data
    """

    print("Fetching policies for location_id:", location_id)
    # Fetch policies from database for the given location
    policies = await sync_to_async(list)(
        Policy.objects.filter(location_id=location_id).order_by('policy_type')
    )

    # Fetch location for context
    location = await sync_to_async(Location.objects.get)(location_id=location_id)

    # Convert to DataFrame to maintain compatibility with existing processing logic
    policy_data = []
    for policy_obj in policies:
        policy_data.append({
            'policy_type': policy_obj.policy_type,
            'details': policy_obj.details,
            'Location': location.location_name
        })

    
    # Create DataFrame
    df = pd.DataFrame(policy_data)

    # Use the existing formatting logic
    if df.empty:
        formatted_policies = "No policies available for this location."
    else:

        # Drop the location column
        df = df.drop(columns=["Location"], errors="ignore")
        
        # Capitalize and format policy types
        df['policy_type'] = df['policy_type'].str.title()

        # Clean up whitespaces/newlines in details
        df['details'] = df['details'].str.replace(r'\s+', ' ', regex=True).str.strip()

        # Build LLM-friendly formatted string
        output = "\n"
        for _, row in df.iterrows():
            output += f"*{row['policy_type']}*:\n{row['details']}.\n\n"

        formatted_policies = output.strip()
    
    # Create structured data for additional use cases
    structured_data = {
        "location_name": location.location_name,
        "location_id": location_id,
        "total_policies": len(policies),
        "policies_by_type": {},
        "policy_ids": [policy.policy_id for policy in policies]
    }
    # Organize policies by type
    for policy_obj in policies:
        policy_type = policy_obj.policy_type
        if policy_type not in structured_data["policies_by_type"]:
            structured_data["policies_by_type"][policy_type] = []
        
        structured_data["policies_by_type"][policy_type].append({
            "policy_id": policy_obj.policy_id,
            "details": policy_obj.details
        })
    
    return {
        "formatted_policies": formatted_policies,
        "structured_data": structured_data,
        "location_name": location.location_name
    }

