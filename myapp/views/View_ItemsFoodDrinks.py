


import json
import csv
import io
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser

from myapp.model.items_food_drinks_model import ItemsFoodDrinks
from myapp.serializers import ItemsFoodDrinksSerializer


# ---------------------------------------------------------------------
# HELPER: ADMIN CHECK (sync-safe)
# ---------------------------------------------------------------------
def require_admin(request):
    auth = JWTAuthentication()
    try:
        user_auth_tuple = auth.authenticate(request)
    except Exception as e:
        return None, JsonResponse({"detail": str(e)}, status=401)

    if not user_auth_tuple:
        return None, JsonResponse(
            {"detail": "Authentication credentials were not provided."}, status=401
        )

    user, token = user_auth_tuple

    if not user.is_authenticated or not user.is_staff:
        return None, JsonResponse(
            {"detail": "You do not have permission to perform this action."}, status=403
        )

    return user, None


# ---------------------------------------------------------------------
# CREATE ITEM
# ---------------------------------------------------------------------
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def create_food_drink_item(request, location_id):
    user, error = require_admin(request)
    if error:
        return error

    try:
        data = request.data.copy()
        data["location"] = location_id

        serializer = ItemsFoodDrinksSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)

        return JsonResponse(serializer.errors, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------------------------------------------------
# GET ALL ITEMS BY LOCATION
# ---------------------------------------------------------------------
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_food_drink_items(request, location_id):
    user, error = require_admin(request)
    if error:
        return error

    items = ItemsFoodDrinks.objects.filter(location_id=location_id)
    serializer = ItemsFoodDrinksSerializer(items, many=True)
    return JsonResponse(serializer.data, safe=False, status=200)


# ---------------------------------------------------------------------
# GET ITEMS GROUPED BY CATEGORY
# ---------------------------------------------------------------------
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_food_drink_items_by_category(request, location_id):
    user, error = require_admin(request)
    if error:
        return error

    items = ItemsFoodDrinks.objects.filter(location_id=location_id).order_by(
        "category_priority", "category", "item"
    )

    grouped = {}
    for item in items:
        cat = item.category

        if cat not in grouped:
            grouped[cat] = {
                "category": cat,
                "category_priority": item.category_priority,
                "category_type": item.category_type,
                "options_type_per_category": item.options_type_per_category,
                "items": [],
            }

        grouped[cat]["items"].append(ItemsFoodDrinksSerializer(item).data)

    result = list(grouped.values())
    result.sort(key=lambda x: x["category_priority"])

    return JsonResponse(result, safe=False, status=200)


# ---------------------------------------------------------------------
# GET SINGLE ITEM
# ---------------------------------------------------------------------
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_food_drink_item(request, location_id, pk):
    user, error = require_admin(request)
    if error:
        return error

    try:
        item = ItemsFoodDrinks.objects.get(item_id=pk, location_id=location_id)
        return JsonResponse(ItemsFoodDrinksSerializer(item).data, status=200)

    except ItemsFoodDrinks.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)


# ---------------------------------------------------------------------
# UPDATE ITEM
# ---------------------------------------------------------------------
@api_view(["PUT", "PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def update_food_drink_item(request, location_id, pk):
    user, error = require_admin(request)
    if error:
        return error

    try:
        item = ItemsFoodDrinks.objects.get(item_id=pk, location_id=location_id)
    except ItemsFoodDrinks.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)

    data = request.data.copy()
    data["location"] = location_id

    serializer = ItemsFoodDrinksSerializer(item, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=200)

    return JsonResponse(serializer.errors, status=400)


# ---------------------------------------------------------------------
# DELETE ITEM
# ---------------------------------------------------------------------
@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def delete_food_drink_item(request, location_id, pk):
    user, error = require_admin(request)
    if error:
        return error

    try:
        item = ItemsFoodDrinks.objects.get(item_id=pk, location_id=location_id)
        item.delete()
        return JsonResponse({"message": "Deleted successfully"}, status=200)

    except ItemsFoodDrinks.DoesNotExist:
        return JsonResponse({"error": "Item not found"}, status=404)


# ---------------------------------------------------------------------
# BULK CREATE USING CSV
# ---------------------------------------------------------------------
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def bulk_create_food_drink_items(request, location_id):
    user, error = require_admin(request)
    if error:
        return error

    if "csv_file" not in request.FILES:
        return JsonResponse({"error": "CSV file is required"}, status=400)

    csv_file = request.FILES["csv_file"]

    if not csv_file.name.endswith(".csv"):
        return JsonResponse({"error": "File must be CSV"}, status=400)

    try:
        csv_text = csv_file.read().decode("utf-8").strip()
        reader = csv.DictReader(io.StringIO(csv_text))

        rows = list(reader)
        created_count = 0
        errors = []

        for idx, row in enumerate(rows, start=2):
            if not any(row.values()):
                continue

            item_data = {
                "location": location_id,
                "category": row.get("Category", "").strip(),
                "item": row.get("Item", "").strip(),
                "price": row.get("Price", "").strip(),
                "category_priority": row.get("category_priority", "0").strip(),
                "category_type": row.get("category_type", "").strip(),
                "options_type_per_category": row.get("options_type_per_category", "").strip(),
                "additional_instructions": row.get("additional_instructions", "").strip(),
                "t_shirt_sizes": row.get("T-Shirt_sizes", "").strip(),
                "t_shirt_type": row.get("T-shirt_type", "").strip(),
                "pitch_in_party_package": row.get("pitch_in_party_package", "").lower()
                in ("yes", "true", "1", "y"),
            }

            if not item_data["category"]:
                errors.append(f"Row {idx}: Category is required")
                continue

            if not item_data["item"]:
                errors.append(f"Row {idx}: Item is required")
                continue

            try:
                item_data["price"] = float(item_data["price"])
            except:
                errors.append(f"Row {idx}: Invalid price")
                continue

            serializer = ItemsFoodDrinksSerializer(data=item_data)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append(f"Row {idx}: {serializer.errors}")

        response = {
            "created_count": created_count,
            "total_rows_processed": len(rows),
            "errors": errors,
        }

        if created_count > 0:
            return JsonResponse(response, status=207 if errors else 201)

        return JsonResponse({"error": "No items created", "errors": errors}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------------------------------------------------
# GET DISTINCT CATEGORIES
# ---------------------------------------------------------------------
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_food_drink_categories(request, location_id):
    user, error = require_admin(request)
    if error:
        return error

    categories = (
        ItemsFoodDrinks.objects.filter(location_id=location_id)
        .values_list("category", flat=True)
        .distinct()
    )

    return JsonResponse({"categories": list(categories)}, status=200)


# ---------------------------------------------------------------------
# GET PARTY PACKAGE ITEMS
# ---------------------------------------------------------------------
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_party_package_items(request, location_id):
    user, error = require_admin(request)
    if error:
        return error

    items = ItemsFoodDrinks.objects.filter(
        location_id=location_id, pitch_in_party_package=True
    )

    return JsonResponse(
        ItemsFoodDrinksSerializer(items, many=True).data,
        safe=False,
        status=200,
    )
