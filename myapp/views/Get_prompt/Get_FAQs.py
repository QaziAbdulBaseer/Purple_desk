


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


