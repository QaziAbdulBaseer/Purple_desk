




import json
import csv
import io
from django.http import JsonResponse
from rest_framework import status
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.group_booking_model import GroupBooking
from myapp.serializers import GroupBookingSerializer

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

async def create_group_booking(request, location_id):
    """Create a new group booking for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # attach FK
        
        serializer = GroupBookingSerializer(data=data)
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

async def get_group_bookings(request, location_id):
    """Get all group bookings for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        bookings = await sync_to_async(lambda: list(
            GroupBooking.objects.filter(location_id=location_id).select_related('location')
        ))()
        serializer = GroupBookingSerializer(bookings, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_group_booking(request, location_id, pk):
    """Get a specific group booking by its primary key and location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        booking = await sync_to_async(GroupBooking.objects.select_related('location').get)(
            group_booking_id=pk, location_id=location_id
        )
        serializer = GroupBookingSerializer(booking)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    except GroupBooking.DoesNotExist:
        return JsonResponse(
            {"error": "Group booking not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_group_booking(request, location_id, pk):
    """Update a group booking"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        booking = await sync_to_async(GroupBooking.objects.get)(
            group_booking_id=pk, location_id=location_id
        )
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # keep FK intact
        
        serializer = GroupBookingSerializer(booking, data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            await sync_to_async(serializer.save)()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        print("This is the error:", serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except GroupBooking.DoesNotExist:
        return JsonResponse(
            {"error": "Group booking not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def delete_group_booking(request, location_id, pk):
    """Delete a group booking"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        booking = await sync_to_async(GroupBooking.objects.get)(
            group_booking_id=pk, location_id=location_id
        )
        await sync_to_async(booking.delete)()
        
        return JsonResponse(
            {"message": "Group booking deleted successfully"}, 
            status=200
        )
    except GroupBooking.DoesNotExist:
        return JsonResponse(
            {"error": "Group booking not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def bulk_create_group_bookings(request, location_id):
    """Bulk create group bookings from CSV file"""
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

            # Extract headers (first row)
            headers = [header.strip().lower().replace(' ', '_') for header in rows[0]]
            
            # Validate required columns
            required_columns = ['group_packages', 'call_flow_priority', 'flat_fee_jumper_price', 'minimum_jumpers']
            missing_headers = [col for col in required_columns if col not in headers]
            
            if missing_headers:
                return JsonResponse(
                    {"error": f"Missing required columns: {', '.join(missing_headers)}. Required columns are: {', '.join(required_columns)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get column indices
            column_mapping = {}
            try:
                for col in ['group_packages', 'call_flow_priority', 'flat_fee_jumper_price', 'minimum_jumpers', 'instruction', 'package_inclusions']:
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
                    booking_data = {
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
                            elif field in ['flat_fee_jumper_price'] and value:
                                try:
                                    value = float(value)
                                except ValueError:
                                    errors.append(f"Row {row_num}: {field} must be a number")
                                    continue
                            booking_data[field] = value

                    # Validate required fields
                    if not booking_data.get('group_packages'):
                        errors.append(f"Row {row_num}: group_packages is required")
                        continue
                    if not booking_data.get('call_flow_priority'):
                        errors.append(f"Row {row_num}: call_flow_priority is required")
                        continue
                    if not booking_data.get('flat_fee_jumper_price'):
                        errors.append(f"Row {row_num}: flat_fee_jumper_price is required")
                        continue
                    if not booking_data.get('minimum_jumpers'):
                        errors.append(f"Row {row_num}: minimum_jumpers is required")
                        continue

                    # Create GroupBooking
                    serializer = GroupBookingSerializer(data=booking_data)
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
                response_data["message"] = f"Successfully created {created_count} group bookings with {len(errors)} errors"
                return JsonResponse(response_data, status=status.HTTP_207_MULTI_STATUS)
            elif created_count > 0:
                response_data["message"] = f"Successfully created {created_count} group bookings"
                return JsonResponse(response_data, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(
                    {"error": f"No group bookings were created. Errors: {', '.join(errors[:5])}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except csv.Error as e:
            return JsonResponse({"error": f"Invalid CSV format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": f"Error processing CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)