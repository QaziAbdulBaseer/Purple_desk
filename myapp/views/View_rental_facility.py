


import json
import csv
import io
from django.http import JsonResponse
from rest_framework import status
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.rental_facility_model import RentalFacility
from myapp.serializers import RentalFacilitySerializer
from myapp.model.locations_model import Location

async def require_admin(request):
    """Reuse the same admin authentication function"""
    try:
        user_auth_tuple = await sync_to_async(JWTAuthentication().authenticate)(request)
    except AuthenticationFailed as e:
        return None, JsonResponse({"detail": str(e)}, status=401)

    if not user_auth_tuple:
        return None, JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

    user, token = user_auth_tuple
    if not user.is_authenticated or not user.is_staff:
        return None, JsonResponse({"detail": "You do not have permission to perform this action."}, status=403)

    return user, None

async def create_rental_facility(request, location_id):
    """Create a new rental facility for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # attach FK
        
        serializer = RentalFacilitySerializer(data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            await sync_to_async(serializer.save)()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        print("This is the error:", serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_rental_facilities(request, location_id):
    """Get all rental facilities for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        facilities = await sync_to_async(lambda: list(
            RentalFacility.objects.filter(location_id=location_id).select_related('location')
        ))()
        serializer = RentalFacilitySerializer(facilities, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_rental_facility(request, location_id, pk):
    """Get a specific rental facility by its primary key and location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        facility = await sync_to_async(RentalFacility.objects.select_related('location').get)(
            rental_facility_id=pk, location_id=location_id
        )
        serializer = RentalFacilitySerializer(facility)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    except RentalFacility.DoesNotExist:
        return JsonResponse(
            {"error": "Rental facility not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_rental_facility(request, location_id, pk):
    """Update a rental facility"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        facility = await sync_to_async(RentalFacility.objects.get)(
            rental_facility_id=pk, location_id=location_id
        )
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # keep FK intact
        
        serializer = RentalFacilitySerializer(facility, data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            await sync_to_async(serializer.save)()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        print("This is the error:", serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except RentalFacility.DoesNotExist:
        return JsonResponse(
            {"error": "Rental facility not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def delete_rental_facility(request, location_id, pk):
    """Delete a rental facility"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        facility = await sync_to_async(RentalFacility.objects.get)(
            rental_facility_id=pk, location_id=location_id
        )
        await sync_to_async(facility.delete)()
        
        return JsonResponse(
            {"message": "Rental facility deleted successfully"}, 
            status=200
        )
    except RentalFacility.DoesNotExist:
        return JsonResponse(
            {"error": "Rental facility not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def bulk_create_rental_facilities(request, location_id):
    """Bulk create rental facilities from CSV file"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        # Check if CSV file is provided
        if 'csv_file' not in request.FILES:
            return JsonResponse({"error": "CSV file is required"}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['csv_file']
        
        # Read and parse CSV file
        try:
            csv_text = await sync_to_async(csv_file.read)()
            csv_text = csv_text.decode('utf-8').strip()
            csv_reader = csv.reader(io.StringIO(csv_text))
            rows = list(csv_reader)
            
            if len(rows) < 2:
                return JsonResponse({"error": "CSV file must contain at least a header row and one data row"}, status=status.HTTP_400_BAD_REQUEST)

            # Extract headers (first row) and normalize them
            headers = [header.strip().lower().replace(' ', '_') for header in rows[0]]
            print("CSV Headers:", headers)  # Debug log
            
            # Updated required columns based on new model
            required_columns = ['rental_jumper_group', 'per_jumper_price', 'minimum_jumpers', 'maximum_jumpers']
            missing_headers = [col for col in required_columns if col not in headers]
            
            if missing_headers:
                return JsonResponse(
                    {"error": f"Missing required columns: {', '.join(missing_headers)}. Required columns are: {', '.join(required_columns)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get column indices - updated for new model
            column_mapping = {}
            expected_columns = ['rental_jumper_group', 'rental_group_name', 'per_jumper_price', 
                              'minimum_jumpers', 'maximum_jumpers', 'inclusions']
            
            for col in expected_columns:
                if col in headers:
                    column_mapping[col] = headers.index(col)
                else:
                    column_mapping[col] = -1

            # Check if we have a location column (optional for validation)
            location_col_index = -1
            if 'location' in headers:
                location_col_index = headers.index('location')

            # Get the location object for validation
            try:
                location_obj = await sync_to_async(Location.objects.get)(location_id=location_id)
            except Location.DoesNotExist:
                return JsonResponse({"error": f"Location with ID {location_id} does not exist"}, 
                                  status=status.HTTP_404_NOT_FOUND)

            # Process data rows
            created_count = 0
            errors = []
            
            for row_num, row in enumerate(rows[1:], start=2):  # start=2 because header is row 1
                try:
                    # Skip empty rows
                    if not any(row):
                        continue

                    # Optional: Validate location name if location column exists
                    if location_col_index != -1 and len(row) > location_col_index:
                        csv_location_name = row[location_col_index].strip()
                        if csv_location_name and csv_location_name.lower() != location_obj.location_name.lower():
                            errors.append(f"Row {row_num}: Location mismatch. CSV says '{csv_location_name}' but uploading to '{location_obj.location_name}'")
                            continue

                    # Extract values with proper indexing
                    facility_data = {
                        'location': location_id
                    }
                    
                    for field, index in column_mapping.items():
                        if index != -1 and len(row) > index:
                            value = row[index].strip() if row[index] else None
                            
                            # Convert to appropriate types
                            if field in ['minimum_jumpers', 'maximum_jumpers'] and value:
                                try:
                                    value = int(value)
                                except ValueError:
                                    errors.append(f"Row {row_num}: {field} must be a whole number")
                                    continue
                            elif field == 'per_jumper_price' and value:
                                try:
                                    value = float(value)
                                except ValueError:
                                    errors.append(f"Row {row_num}: {field} must be a number")
                                    continue
                            
                            facility_data[field] = value
                        else:
                            facility_data[field] = None

                    # Validate required fields
                    if not facility_data.get('rental_jumper_group'):
                        errors.append(f"Row {row_num}: rental_jumper_group is required")
                        continue
                    
                    if not facility_data.get('per_jumper_price') and facility_data.get('per_jumper_price') != 0:
                        errors.append(f"Row {row_num}: per_jumper_price is required")
                        continue
                    
                    if not facility_data.get('minimum_jumpers'):
                        errors.append(f"Row {row_num}: minimum_jumpers is required")
                        continue
                    
                    if not facility_data.get('maximum_jumpers'):
                        # Handle empty maximum_jumpers by setting it equal to minimum_jumpers
                        if facility_data.get('minimum_jumpers'):
                            facility_data['maximum_jumpers'] = facility_data['minimum_jumpers']
                        else:
                            errors.append(f"Row {row_num}: maximum_jumpers is required")
                            continue

                    # Validate that maximum_jumpers >= minimum_jumpers
                    if (facility_data.get('maximum_jumpers') and facility_data.get('minimum_jumpers') and
                        facility_data['maximum_jumpers'] < facility_data['minimum_jumpers']):
                        errors.append(f"Row {row_num}: maximum_jumpers ({facility_data['maximum_jumpers']}) cannot be less than minimum_jumpers ({facility_data['minimum_jumpers']})")
                        continue

                    # Convert per_jumper_price to Decimal with 2 decimal places
                    if 'per_jumper_price' in facility_data and facility_data['per_jumper_price'] is not None:
                        from decimal import Decimal
                        facility_data['per_jumper_price'] = Decimal(str(round(facility_data['per_jumper_price'], 2)))

                    # Create or update RentalFacility (update if combination of location and rental_jumper_group exists)
                    try:
                        # Check if a facility with same location and rental_jumper_group already exists
                        existing_facility = await sync_to_async(
                            lambda: RentalFacility.objects.filter(
                                location_id=location_id,
                                rental_jumper_group=facility_data['rental_jumper_group']
                            ).first()
                        )()
                        
                        if existing_facility:
                            # Update existing facility
                            serializer = RentalFacilitySerializer(existing_facility, data=facility_data)
                        else:
                            # Create new facility
                            serializer = RentalFacilitySerializer(data=facility_data)
                        
                        is_valid = await sync_to_async(serializer.is_valid)()
                        
                        if is_valid:
                            await sync_to_async(serializer.save)()
                            created_count += 1
                        else:
                            # Format serializer errors
                            error_messages = []
                            for field, field_errors in serializer.errors.items():
                                if isinstance(field_errors, list):
                                    for error in field_errors:
                                        error_messages.append(f"{field}: {error}")
                                else:
                                    error_messages.append(f"{field}: {field_errors}")
                            errors.append(f"Row {row_num}: {', '.join(error_messages)}")

                    except Exception as e:
                        errors.append(f"Row {row_num}: Database error - {str(e)}")

                except Exception as e:
                    errors.append(f"Row {row_num}: Unexpected error - {str(e)}")

            response_data = {
                "created_count": created_count,
                "total_rows_processed": len(rows) - 1,
                "errors": errors[:50]  # Limit errors to first 50 to avoid huge responses
            }

            if created_count > 0 and errors:
                response_data["message"] = f"Successfully created/updated {created_count} rental facilities with {len(errors)} errors"
                return JsonResponse(response_data, status=status.HTTP_207_MULTI_STATUS)
            elif created_count > 0:
                response_data["message"] = f"Successfully created/updated {created_count} rental facilities"
                return JsonResponse(response_data, status=status.HTTP_201_CREATED)
            else:
                if errors:
                    return JsonResponse(
                        {"error": f"No rental facilities were created/updated. First 5 errors: {', '.join(errors[:5])}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    return JsonResponse(
                        {"error": "No rental facilities were created/updated. No valid data found."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

        except csv.Error as e:
            return JsonResponse({"error": f"Invalid CSV format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": f"Error processing CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        import traceback
        print(f"Bulk upload error: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



