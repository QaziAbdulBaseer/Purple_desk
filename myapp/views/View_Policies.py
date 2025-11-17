



import json
import csv
import io
from django.http import JsonResponse
from rest_framework import status
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.policy_model import Policy
from myapp.serializers import PolicySerializer

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

async def create_policy(request, location_id):
    """Create a new policy for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # attach FK
        
        serializer = PolicySerializer(data=data)
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

async def get_policies(request, location_id):
    """Get all policies for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        policies = await sync_to_async(lambda: list(
            Policy.objects.filter(location_id=location_id)
        ))()
        serializer = PolicySerializer(policies, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_policy(request, location_id, pk):
    """Get a specific policy by its primary key and location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        policy = await sync_to_async(Policy.objects.get)(
            policy_id=pk, location_id=location_id
        )
        serializer = PolicySerializer(policy)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    except Policy.DoesNotExist:
        return JsonResponse(
            {"error": "Policy not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_policy(request, location_id, pk):
    """Update a policy"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        policy = await sync_to_async(Policy.objects.get)(
            policy_id=pk, location_id=location_id
        )
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # keep FK intact
        
        serializer = PolicySerializer(policy, data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            await sync_to_async(serializer.save)()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        print("This is the error:", serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Policy.DoesNotExist:
        return JsonResponse(
            {"error": "Policy not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def delete_policy(request, location_id, pk):
    """Delete a policy"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        policy = await sync_to_async(Policy.objects.get)(
            policy_id=pk, location_id=location_id
        )
        await sync_to_async(policy.delete)()
        
        return JsonResponse(
            {"message": "Policy deleted successfully"}, 
            status=200
        )
    except Policy.DoesNotExist:
        return JsonResponse(
            {"error": "Policy not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def bulk_create_policies(request, location_id):
    """Bulk create policies from CSV file"""
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
            # csv_text = csv_text.decode('utf-8').strip()
            csv_text = csv_text.decode('utf-8-sig').strip()
            
            # Use csv.reader with proper quote handling
            csv_reader = csv.reader(io.StringIO(csv_text))
            rows = list(csv_reader)
            
            if len(rows) < 2:
                return JsonResponse({"error": "CSV file must contain at least a header row and one data row"}, status=status.HTTP_400_BAD_REQUEST)

            # Extract headers (first row)
            headers = [header.strip().lower() for header in rows[0]]
            
            # Validate required columns
            required_columns = ['policy_type', 'details']
            missing_headers = [col for col in required_columns if col not in headers]
            
            if missing_headers:
                return JsonResponse(
                    {"error": f"Missing required columns: {', '.join(missing_headers)}. Required columns are: {', '.join(required_columns)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get column indices
            try:
                type_index = headers.index('policy_type')
                details_index = headers.index('details')
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
                    if not any(row) or len(row) < max(type_index, details_index) + 1:
                        continue

                    # Extract values with proper indexing
                    policy_type = row[type_index].strip() if len(row) > type_index else ''
                    details = row[details_index].strip() if len(row) > details_index else ''

                    # Validate required fields
                    if not policy_type:
                        errors.append(f"Row {row_num}: policy_type is required")
                        continue
                    if not details:
                        errors.append(f"Row {row_num}: details is required")
                        continue

                    # Validate field lengths
                    if len(policy_type) > 255:
                        errors.append(f"Row {row_num}: policy_type cannot exceed 255 characters")
                        continue
                    if len(details) > 5000:
                        errors.append(f"Row {row_num}: details cannot exceed 5000 characters")
                        continue

                    # Create Policy
                    policy_data = {
                        'location': location_id,
                        'policy_type': policy_type,
                        'details': details
                    }

                    serializer = PolicySerializer(data=policy_data)
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
                response_data["message"] = f"Successfully created {created_count} policies with {len(errors)} errors"
                return JsonResponse(response_data, status=status.HTTP_207_MULTI_STATUS)
            elif created_count > 0:
                response_data["message"] = f"Successfully created {created_count} policies"
                return JsonResponse(response_data, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse(
                    {"error": f"No policies were created. Errors: {', '.join(errors[:5])}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except csv.Error as e:
            return JsonResponse({"error": f"Invalid CSV format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": f"Error processing CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_policy_types(request, location_id):
    """Get unique policy types for a location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        policies = await sync_to_async(lambda: list(
            Policy.objects.filter(location_id=location_id)
        ))()
        
        policy_types = list(set([policy.policy_type for policy in policies]))
        policy_types.sort()
        
        return JsonResponse({"policy_types": policy_types}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)