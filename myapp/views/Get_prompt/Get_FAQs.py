
# # hi, first i am looking data from the google sheet. but now i have a database.
# # so i want to update this function to get data from database instead of google sheet.
# # but keep the data processing logic same as before.
# # just change the data fetching part. now fetch data from FAQ model in database.

# # i also give you an example code for the Membership info fetching from database.


# import asyncio
# import pandas as pd
# from datetime import datetime, timedelta, date
# from typing import List, Tuple, Dict, Optional
# from concurrent.futures import ThreadPoolExecutor
# import pytz

# # Import your Django models
# from myapp.model.hours_of_operations_model import HoursOfOperation
# from asgiref.sync import sync_to_async
# from myapp.model.faqs_model import FAQ


# async def extract_faqs_for_llm(df: pd.DataFrame) -> str:
#     summary = []
    
#     grouped = df.groupby('question_type')

#     for category, group in grouped:
#         summary.append(f"### {category.title()} FAQs:\n")
#         for _, row in group.iterrows():
#             question = row.get("question", "").strip()
#             answer = row.get("answer", "").strip()

#             if question and answer:
#                 summary.append(f"*Question:* {question}\n*Answer:* {answer}.\n")

#     return "\n".join(summary)




import asyncio
import pandas as pd
from datetime import datetime, timedelta, date
from typing import List, Tuple, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import pytz

from asgiref.sync import sync_to_async
from myapp.model.faqs_model import FAQ






async def extract_faqs_for_llm(location_id: int) -> str:
    """
    Extract FAQs from database and format them for LLM
    
    Args:
        location_id: The location ID to fetch FAQs for
    
    Returns:
        Formatted string with all FAQs for the location
    """

    print("Fetching FAQs from database...")
    # Fetch FAQs from database for the given location
    faqs = await sync_to_async(list)(
        FAQ.objects.filter(location_id=location_id).order_by('question_type', 'faq_id')
    )
    
    # Convert to DataFrame to maintain compatibility with existing processing logic
    faq_data = []
    for faq_obj in faqs:
        faq_data.append({
            'question_type': faq_obj.question_type,
            'question': faq_obj.question,
            'answer': faq_obj.answer
        })
    
    # Create DataFrame with the same structure as before
    df = pd.DataFrame(faq_data)
    
    # Use the existing data processing logic (same as before)
    summary = []
    
    # Check if DataFrame is empty
    if df.empty:
        return "No FAQs available for this location."
    
    grouped = df.groupby('question_type')

    for category, group in grouped:
        summary.append(f"### {category.title()} FAQs:\n")
        for _, row in group.iterrows():
            question = row.get("question", "").strip()
            answer = row.get("answer", "").strip()

            if question and answer:
                summary.append(f"*Question:* {question}\n*Answer:* {answer}.\n")

    return "\n".join(summary)