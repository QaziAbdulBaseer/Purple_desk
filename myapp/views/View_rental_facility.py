import json
from django.http import JsonResponse
from rest_framework import status
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.rental_facility_model import RentalFacility
from myapp.serializers import RentalFacilitySerializer

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
        import csv
        import io
        
        try:
            csv_text = await sync_to_async(csv_file.read)()
            csv_text = csv_text.decode('utf-8').strip()
            csv_reader = csv.reader(io.StringIO(csv_text))
            rows = list(csv_reader)
            
            if len(rows) < 2:
                return JsonResponse({"error": "CSV file must contain at least a header row and one data row"}, status=status.HTTP_400_BAD_REQUEST)

            # Extract headers (first row)
            headers = [header.strip().lower().replace(' ', '_') for header in rows[0]]
            
            # Validate required columns
            required_columns = ['rental_jumper_group', 'call_flow_priority', 'per_jumper_price', 'minimum_jumpers']
            missing_headers = [col for col in required_columns if col not in headers]
            
            if missing_headers:
                return JsonResponse(
                    {"error": f"Missing required columns: {', '.join(missing_headers)}. Required columns are: {', '.join(required_columns)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get column indices
            column_mapping = {}
            try:
                for col in ['rental_jumper_group', 'call_flow_priority', 'per_jumper_price', 'minimum_jumpers', 'instruction', 'inclusions']:
                    if col in headers:
                        column_mapping[col] = headers.index(col)
                    else:
                        column_mapping[col] = -1
            except ValueError as e:
                return JsonResponse(
                    {"error": f"Column not found: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process data rows
            created_count = 0
            errors = []
            
            for row_num, row in enumerate(rows[1:], start=2):  # start=2 because header is row 1
                try:
                    # Skip empty rows
                    if not any(row):
                        continue

                    # Extract values with proper indexing
                    facility_data = {
                        'location': location_id
                    }
                    
                    for field, index in column_mapping.items():
                        if index != -1 and len(row) > index:
                            value = row[index].strip() if row[index] else None
                            if field in ['call_flow_priority', 'minimum_jumpers'] and value:
                                try:
                                    value = int(value)
                                except ValueError:
                                    errors.append(f"Row {row_num}: {field} must be a whole number")
                                    continue
                            elif field in ['per_jumper_price'] and value:
                                try:
                                    value = float(value)
                                except ValueError:
                                    errors.append(f"Row {row_num}: {field} must be a number")
                                    continue
                            facility_data[field] = value

                    # Validate required fields
                    if not facility_data.get('rental_jumper_group'):
                        errors.append(f"Row {row_num}: rental_jumper_group is required")
                        continue
                    if not facility_data.get('call_flow_priority'):
                        errors.append(f"Row {row_num}: call_flow_priority is required")
                        continue
                    if not facility_data.get('per_jumper_price'):
                        errors.append(f"Row {row_num}: per_jumper_price is required")
                        continue
                    if not facility_data.get('minimum_jumpers'):
                        errors.append(f"Row {row_num}: minimum_jumpers is required")
                        continue

                    # Create RentalFacility
                    serializer = RentalFacilitySerializer(data=facility_data)
                    is_valid = await sync_to_async(serializer.is_valid)()
                    
                    if is_valid:
                        await sync_to_async(serializer.save)()
                        created_count += 1
                    else:
                        # Format serializer errors
                        error_messages = []
                        for field, field_errors in serializer.errors.items():
                            for error in field_errors:
                                error_messages.append(f"{field}: {error}")
                        errors.append(f"Row {row_num}: {', '.join(error_messages)}")

                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")

            response_data = {
                "created_count": created_count,
                "total_rows_processed": len(rows) - 1,
                "errors": errors
            }

            if created_count > 0 and errors:
                response_data["message"] = f"Successfully created {created_count} rental facilities with {len(errors)} errors"
                return JsonResponse(response_data, status=status.HTTP_207_MULTI_STATUS)
            elif created_count > 0:
                response_data["message"] = f"Successfully created {created_count} rental facilities"
                return JsonResponse(response_data, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(
                    {"error": f"No rental facilities were created. Errors: {', '.join(errors[:5])}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except csv.Error as e:
            return JsonResponse({"error": f"Invalid CSV format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": f"Error processing CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




