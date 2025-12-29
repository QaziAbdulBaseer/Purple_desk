# import os
# from datetime import datetime
# from django.conf import settings
# import re

# def sanitize_filename(name):
#     """Sanitize string for use in folder/filenames"""
#     # Remove or replace invalid characters
#     sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
#     # Replace multiple spaces with single underscore
#     sanitized = re.sub(r'\s+', '_', sanitized)
#     # Remove leading/trailing spaces and underscores
#     sanitized = sanitized.strip('_')
#     return sanitized

# def create_location_folder(location_id, location_name=None):
#     """
#     Create a folder with location_id, location_name and current datetime
#     Format: {location_id}_{location_name}_{YYYYMMDD_HHMMSS}
#     """
#     # If location_name is not provided, use a placeholder
#     if not location_name:
#         location_name = f"Location_{location_id}"
    
#     # Sanitize location name
#     sanitized_location_name = sanitize_filename(location_name)
    
#     current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
#     folder_name = f"{location_id}_{sanitized_location_name}_{current_datetime}"
    
#     # Create folder in a dedicated directory
#     folder_path = os.path.join(settings.BASE_DIR, 'generated_prompts', folder_name)
#     os.makedirs(folder_path, exist_ok=True)
    
#     return folder_name, folder_path

# def save_markdown_file(folder_path, filename, content):
#     """
#     Save content to a markdown file in the specified folder
#     """
#     file_path = os.path.join(folder_path, filename)
    
#     with open(file_path, 'w', encoding='utf-8') as f:
#         f.write(content)
    
#     return file_path

# def read_markdown_file(file_path):
#     """
#     Read content from a markdown file
#     """
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             return f.read()
#     except FileNotFoundError:
#         return ""

# # def combine_all_prompts(folder_path=r"D:\Sybrid\purple_desk\New_purple_desk\New_purple_desk_backend\generated_prompts\1_Location_1_20251216_160241" , location_id=1, search_number=2222, client_id=1):
# #     """
# #     Combine all prompt files in a folder into one markdown file
# #     """
# #     print("Combining all prompts...")
# #     prompt_files = [
# #         'starting_guidelines_prompt.md',
# #         'current_time_info_prompt.md',
# #         'current_date_prompt.md',
# #         'birthday_party_package_prompt.md',
# #         'jump_pass_prompt.md',
# #         'jump_pass_info_prompt.md',
# #         'membership_prompt.md',
# #         'membership_info_prompt.md',
# #         'hours_of_operation_prompt.md',
# #         'faqs_prompt.md',
# #         'policies_prompt.md',
# #         'rental_facility_prompt.md',
# #         'location_info_prompt.md'
# #     ]
    
# #     combined_content = "# Combined All Prompts\n\n"
# #     combined_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
# #     files_found = []
    
# #     for prompt_file in prompt_files:
# #         file_path = os.path.join(folder_path, prompt_file)
# #         if os.path.exists(file_path):
# #             content = read_markdown_file(file_path)
# #             if content:
# #                 files_found.append(prompt_file)
# #                 combined_content += f"## {prompt_file.replace('_', ' ').replace('.md', '').title()}\n\n"
# #                 combined_content += content
# #                 combined_content += "\n\n---\n\n"
    
# #     # Save the combined file
# #     combined_file_path = os.path.join(folder_path, 'combined_all_prompts.md')
# #     with open(combined_file_path, 'w', encoding='utf-8') as f:
# #         f.write(combined_content)
    
# #     return combined_content, combined_file_path, files_found






# # async def combine_all_prompts(folder_path, location_id, search_number, client_id):
# #     print("Combining all prompts...")

# #     prompt_files = [
# #         'starting_guidelines_prompt.md',
# #         'current_time_info_prompt.md',
# #         'current_date_prompt.md',
# #         'birthday_party_package_prompt.md',
# #         'jump_pass_prompt.md',
# #         'jump_pass_info_prompt.md',
# #         'membership_prompt.md',
# #         'membership_info_prompt.md',
# #         'hours_of_operation_prompt.md',
# #         'faqs_prompt.md',
# #         'policies_prompt.md',
# #         'rental_facility_prompt.md',
# #         'location_info_prompt.md'
# #     ]

# #     combined_content = "# Combined All Prompts\n\n"
# #     combined_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

# #     files_found = []

# #     for prompt_file in prompt_files:
# #         file_path = os.path.join(folder_path, prompt_file)
# #         if os.path.exists(file_path):
# #             content = read_markdown_file(file_path)
# #             if content:
# #                 files_found.append(prompt_file)
# #                 combined_content += f"## {prompt_file.replace('_', ' ').replace('.md', '').title()}\n\n"
# #                 combined_content += content + "\n\n---\n\n"

# #     combined_file_path = os.path.join(folder_path, 'combined_all_prompts.md')
# #     with open(combined_file_path, 'w', encoding='utf-8') as f:
# #         f.write(combined_content)

# #     return combined_content, combined_file_path, files_found







# # from django.conf import settings
# # import os
# # from datetime import datetime
# # from django.http import JsonResponse

# # async def combine_all_prompts(request, location_id, search_number, client_id):
# #     print("Combining all prompts...")
# #     print("this is the base dir === " , settings.BASE_DIR)
# #     # folder_path = os.path.join(
# #     #     settings.BASE_DIR + r"generated_prompts",
# #     #     "1_Location_1_20251216_160241",
# #     #     str(client_id),
# #     #     str(location_id),
# #     #     str(search_number),
# #     # )
# #     folder_path = os.path.join(
# #         str(settings.BASE_DIR),
# #         "generated_prompts",
# #         "1_Location_1_20251216_160241",
# #         str(client_id),
# #         str(location_id),
# #         str(search_number),
# #     )


# #     prompt_files = [
# #         'starting_guidelines_prompt.md',
# #         'current_time_info_prompt.md',
# #         'current_date_prompt.md',
# #         'birthday_party_package_prompt.md',
# #         'jump_pass_prompt.md',
# #         'jump_pass_info_prompt.md',
# #         'membership_prompt.md',
# #         'membership_info_prompt.md',
# #         'hours_of_operation_prompt.md',
# #         'faqs_prompt.md',
# #         'policies_prompt.md',
# #         'rental_facility_prompt.md',
# #         'location_info_prompt.md'
# #     ]

# #     combined_content = "# Combined All Prompts\n\n"
# #     combined_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

# #     files_found = []

# #     for prompt_file in prompt_files:
# #         file_path = os.path.join(folder_path, prompt_file)
# #         if os.path.exists(file_path):
# #             content = read_markdown_file(file_path)
# #             if content:
# #                 files_found.append(prompt_file)
# #                 combined_content += f"## {prompt_file.replace('_', ' ').replace('.md', '').title()}\n\n"
# #                 combined_content += content + "\n\n---\n\n"

# #     combined_file_path = os.path.join(folder_path, 'combined_all_prompts.md')
# #     os.makedirs(folder_path, exist_ok=True)

# #     with open(combined_file_path, 'w', encoding='utf-8') as f:
# #         f.write(combined_content)

# #     return JsonResponse({
# #         "content": combined_content,
# #         "file_path": combined_file_path,
# #         "files_found": files_found
# #     })







# from django.conf import settings
# from pathlib import Path
# from datetime import datetime
# from django.http import JsonResponse


# def read_markdown_file(file_path: Path):
#     try:
#         return file_path.read_text(encoding="utf-8")
#     except Exception:
#         return None


# async def combine_all_prompts(request, location_id, search_number, client_id):
#     print("Combining all prompts...")
#     print("BASE_DIR =", settings.BASE_DIR)

#     # Step 1: Base generated_prompts directory
#     base_prompts_dir = Path(settings.BASE_DIR) / "generated_prompts"

#     if not base_prompts_dir.exists():
#         return JsonResponse(
#             {"error": "generated_prompts folder not found"},
#             status=404
#         )

#     # Step 2: Find the location folder dynamically
#     # Example: 1_Location_1_20251216_160241
#     location_folders = list(base_prompts_dir.glob("*Location*"))

#     if not location_folders:
#         return JsonResponse(
#             {"error": "No location folder found"},
#             status=404
#         )

#     # Pick the first (or latest if you want)
#     folder_path = location_folders[0]

#     print("Using folder:", folder_path)

#     prompt_files = [
#         "starting_guidelines_prompt.md",
#         "current_time_info_prompt.md",
#         "current_date_prompt.md",
#         "birthday_party_package_prompt.md",
#         "membership_info_prompt.md",
#         "membership_prompt.md",
#         "jump_pass_info_prompt.md",
#         "jump_pass_prompt.md",
#         "location_info_prompt.md",
#         "faqs_prompt.md",
#         "policies_prompt.md",
#         "hours_of_operation_prompt.md",
#         "rental_facility_prompt.md",
#     ]

#     combined_content = "# Combined All Prompts\n\n"
#     combined_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

#     files_found = []

#     # Step 3: Read files
#     for prompt_file in prompt_files:
#         file_path = folder_path / prompt_file
#         if file_path.exists():
#             content = read_markdown_file(file_path)
#             if content:
#                 files_found.append(prompt_file)
#                 combined_content += (
#                     f"## {prompt_file.replace('_', ' ').replace('.md', '').title()}\n\n"
#                 )
#                 combined_content += content + "\n\n---\n\n"

#     # Step 4: Write combined file
#     combined_file_path = folder_path / "combined_all_prompts.md"

#     combined_file_path.write_text(combined_content, encoding="utf-8")

#     return JsonResponse({
#         "content": combined_content,
#         "file_path": str(combined_file_path),
#         "files_found": files_found,
#     })








# myapp/utils/prompt_file_utils.py
import os
from datetime import datetime
from django.conf import settings
import re

def sanitize_filename(name):
    """Sanitize string for use in folder/filenames"""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Replace multiple spaces with single underscore
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Remove leading/trailing spaces and underscores
    sanitized = sanitized.strip('_')
    return sanitized

def get_location_folder_path(location_id, location_name=None):
    """
    Get or create folder path for a location
    Format: {location_id}_{location_name}
    """
    # If location_name is not provided, use a placeholder
    if not location_name:
        location_name = f"Location_{location_id}"
    
    # Sanitize location name
    sanitized_location_name = sanitize_filename(location_name)
    folder_name = f"{location_id}_{sanitized_location_name}"
    
    # Create folder in a dedicated directory
    folder_path = os.path.join(settings.BASE_DIR, 'generated_prompts', folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    return folder_name, folder_path

def save_markdown_file(folder_path, filename, content):
    """
    Save content to a markdown file in the specified folder
    """
    file_path = os.path.join(folder_path, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path

def read_markdown_file(file_path):
    """
    Read content from a markdown file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def combine_all_prompts_for_location(location_id, location_name=None):
    """
    Combine all prompt files for a specific location into one markdown file
    Returns: combined_content, combined_file_path, files_found
    """
    # Get the location folder path
    folder_name, folder_path = get_location_folder_path(location_id, location_name)
    
    print(f"Combining prompts for location {location_id} from folder: {folder_path}")
    
    # Define all possible prompt files for a location
    prompt_files = [
        'starting_guidelines_prompt.md',
        'current_time_info_prompt.md',
        'current_date_prompt.md',
        'current_time_prompt.md',
        'birthday_party_package_prompt.md',
        'jump_pass_prompt.md',
        'jump_pass_info_prompt.md',
        'membership_prompt.md',
        'membership_info_prompt.md',
        'hours_of_operation_prompt.md',
        'faqs_prompt.md',
        'policies_prompt.md',
        'rental_facility_prompt.md',
        'location_info_prompt.md',
        'prompt_variables.md'
    ]
    
    combined_content = "# Combined All Prompts\n\n"
    combined_content += f"Location ID: {location_id}\n"
    if location_name:
        combined_content += f"Location Name: {location_name}\n"
    combined_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    combined_content += "=" * 50 + "\n\n"
    
    files_found = []
    
    for prompt_file in prompt_files:
        file_path = os.path.join(folder_path, prompt_file)
        if os.path.exists(file_path):
            content = read_markdown_file(file_path)
            if content.strip():
                files_found.append(prompt_file)
                combined_content += f"## {prompt_file.replace('_', ' ').replace('.md', '').title()}\n\n"
                combined_content += content
                combined_content += "\n\n" + "=" * 50 + "\n\n"
    
    # Save the combined file
    combined_file_path = os.path.join(folder_path, 'combined_all_prompts.md')
    with open(combined_file_path, 'w', encoding='utf-8') as f:
        f.write(combined_content)
    
    return combined_content, combined_file_path, files_found

def get_location_files_info(location_id, location_name=None):
    """
    Get information about all files in a location folder
    """
    folder_name, folder_path = get_location_folder_path(location_id, location_name)
    
    files_info = []
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and filename.endswith('.md'):
                file_stat = os.stat(file_path)
                files_info.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'created': datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                })
    
    return {
        'folder_name': folder_name,
        'folder_path': folder_path,
        'files': files_info,
        'total_files': len(files_info)
    }


