import json
import csv
import io
from django.http import JsonResponse
from rest_framework import status
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.promotions_model import Promotion
from myapp.serializers import PromotionSerializer

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

async def create_promotion(request, location_id):
    """Create a new promotion for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # attach FK
        
        serializer = PromotionSerializer(data=data)
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

async def get_promotions(request, location_id):
    """Get all promotions for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        promotions = await sync_to_async(lambda: list(
            Promotion.objects.filter(location_id=location_id)
        ))()
        serializer = PromotionSerializer(promotions, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_active_promotions(request, location_id):
    """Get active promotions for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        # Get all promotions and filter active ones in Python
        promotions = await sync_to_async(lambda: list(
            Promotion.objects.filter(location_id=location_id)
        ))()
        
        active_promotions = [promo for promo in promotions if promo.is_active()]
        serializer = PromotionSerializer(active_promotions, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_promotion(request, location_id, pk):
    """Get a specific promotion by its primary key and location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        promotion = await sync_to_async(Promotion.objects.get)(
            promotion_id=pk, location_id=location_id
        )
        serializer = PromotionSerializer(promotion)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    except Promotion.DoesNotExist:
        return JsonResponse(
            {"error": "Promotion not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_promotion(request, location_id, pk):
    """Update a promotion"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        promotion = await sync_to_async(Promotion.objects.get)(
            promotion_id=pk, location_id=location_id
        )
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # keep FK intact
        
        serializer = PromotionSerializer(promotion, data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            await sync_to_async(serializer.save)()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        print("This is the error:", serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Promotion.DoesNotExist:
        return JsonResponse(
            {"error": "Promotion not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def delete_promotion(request, location_id, pk):
    """Delete a promotion"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        promotion = await sync_to_async(Promotion.objects.get)(
            promotion_id=pk, location_id=location_id
        )
        await sync_to_async(promotion.delete)()
        
        return JsonResponse(
            {"message": "Promotion deleted successfully"}, 
            status=200
        )
    except Promotion.DoesNotExist:
        return JsonResponse(
            {"error": "Promotion not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def bulk_create_promotions(request, location_id):
    """Bulk create promotions from CSV file"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        # Check if CSV file is provided
        if 'csv_file' not in request.FILES:
            return JsonResponse({"error": "CSV file is required"}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['csv_file']
        
        # Validate file type
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({"error": "File must be a CSV"}, status=status.HTTP_400_BAD_REQUEST)

        # Read and parse CSV file
        try:
            csv_text = await sync_to_async(csv_file.read)()
            csv_text = csv_text.decode('utf-8').strip()
            
            # Use csv.reader with proper quote handling
            csv_reader = csv.reader(io.StringIO(csv_text))
            rows = list(csv_reader)
            
            if len(rows) < 2:
                return JsonResponse({"error": "CSV file must contain at least a header row and one data row"}, status=status.HTTP_400_BAD_REQUEST)

            # Extract headers (first row)
            headers = [header.strip().lower().replace(' ', '_') for header in rows[0]]
            
            # Validate required columns
            required_columns = ['promotion_code', 'title', 'details', 'category']
            missing_headers = [col for col in required_columns if col not in headers]
            
            if missing_headers:
                return JsonResponse(
                    {"error": f"Missing required columns: {', '.join(missing_headers)}. Required columns are: {', '.join(required_columns)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get column indices
            column_mapping = {}
            try:
                for col in ['start_date', 'end_date', 'start_day', 'end_day', 'start_time', 'end_time', 
                           'schedule_type', 'promotion_code', 'title', 'details', 'category', 'sub_category',
                           'eligibility_type', 'constraint_value', 'instructions']:
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
                    promotion_data = {
                        'location': location_id
                    }
                    
                    for field, index in column_mapping.items():
                        if index != -1 and len(row) > index:
                            value = row[index].strip() if row[index] else None
                            if field in ['constraint_value'] and value:
                                try:
                                    value = float(value)
                                except ValueError:
                                    errors.append(f"Row {row_num}: {field} must be a number")
                                    continue
                            promotion_data[field] = value

                    # Validate required fields
                    if not promotion_data.get('promotion_code'):
                        errors.append(f"Row {row_num}: promotion_code is required")
                        continue
                    if not promotion_data.get('title'):
                        errors.append(f"Row {row_num}: title is required")
                        continue
                    if not promotion_data.get('details'):
                        errors.append(f"Row {row_num}: details is required")
                        continue
                    if not promotion_data.get('category'):
                        errors.append(f"Row {row_num}: category is required")
                        continue

                    # Create Promotion
                    serializer = PromotionSerializer(data=promotion_data)
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
                response_data["message"] = f"Successfully created {created_count} promotions with {len(errors)} errors"
                return JsonResponse(response_data, status=status.HTTP_207_MULTI_STATUS)
            elif created_count > 0:
                response_data["message"] = f"Successfully created {created_count} promotions"
                return JsonResponse(response_data, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(
                    {"error": f"No promotions were created. Errors: {', '.join(errors[:5])}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except csv.Error as e:
            return JsonResponse({"error": f"Invalid CSV format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": f"Error processing CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_promotion_categories(request, location_id):
    """Get unique promotion categories for a location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        categories = await sync_to_async(lambda: list(
            Promotion.objects.filter(location_id=location_id)
            .values_list('category', flat=True)
            .distinct()
        ))()
        
        return JsonResponse({"categories": categories}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)