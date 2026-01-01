# views/roller_products_view.py or add to your existing views file
import json
import logging
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
import requests
from datetime import datetime, timedelta

from myapp.model.locations_model import Location
from myapp.utils.roller_token_manager import get_or_refresh_roller_token

logger = logging.getLogger(__name__)


class RollerProductsAPI(APIView):
    """
    API to fetch Roller products by location ID
    GET /api/roller-products/?location_id=<id>&product_category=<category>&force_refresh=true
    
    Note: Products are cached for 24 hours by default since they don't change frequently
    """
    
    # Choose appropriate permission - AllowAny for public API or IsAuthenticated for protected
    permission_classes = [AllowAny]  # Change to [IsAuthenticated] if needed
    
    # Cache for 24 hours (86400 seconds)
    CACHE_TIMEOUT = 86400
    
    def get_cache_key(self, location_id, product_category=None):
        """Generate cache key for products"""
        if product_category:
            return f"roller_products_{location_id}_{product_category}"
        return f"roller_products_{location_id}"
    
    def get(self, request):
        """
        Get Roller products for a specific location
        
        Query Parameters:
        - location_id (required): ID of the location
        - product_category (optional): Filter products by category (e.g., 'Merchandise', 'PartyPackage')
        - force_refresh (optional, default=false): Force refresh from API ignoring cache
        
        Returns:
        - List of Roller products with details
        """
        try:
            # Get query parameters
            location_id = request.query_params.get('location_id')
            product_category = request.query_params.get('product_category')
            force_refresh = request.query_params.get('force_refresh', 'false').lower() == 'true'
            
            # Validate required parameters
            if not location_id:
                return Response({
                    'success': False,
                    'message': 'location_id is required as query parameter'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get location
            try:
                location = Location.objects.get(location_id=location_id)
                logger.info(f"Fetching Roller products for location: {location.location_name} (ID: {location_id})")
            except Location.DoesNotExist:
                logger.error(f"Location with ID {location_id} not found")
                return Response({
                    'success': False,
                    'message': f'Location with ID {location_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check cache first (unless force refresh)
            cache_key = self.get_cache_key(location_id, product_category)
            if not force_refresh:
                cached_products = cache.get(cache_key)
                if cached_products:
                    logger.info(f"Returning cached products for location {location_id}")
                    return Response({
                        'success': True,
                        'message': 'Products retrieved from cache',
                        'data': cached_products,
                        'metadata': {
                            'cached': True,
                            'cached_at': cache.get(f"{cache_key}_timestamp"),
                            'location_id': location_id,
                            'location_name': location.location_name,
                            'product_count': len(cached_products),
                            'product_category': product_category
                        }
                    })
            
            # Get Roller API token
            roller_token = get_or_refresh_roller_token(location)
            print("This is roller token:", roller_token)
            if not roller_token:
                logger.error(f"Failed to get Roller token for location {location_id}")
                return Response({
                    'success': False,
                    'message': 'Failed to authenticate with Roller API'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Fetch products from Roller API
            products = self._fetch_roller_products(roller_token, product_category)
            
            if products is None:
                return Response({
                    'success': False,
                    'message': 'Failed to fetch products from Roller API'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Filter and format products if needed
            formatted_products = self._format_products(products, location_id)
            
            # Cache the results
            cache.set(cache_key, formatted_products, self.CACHE_TIMEOUT)
            cache.set(f"{cache_key}_timestamp", datetime.now().isoformat(), self.CACHE_TIMEOUT)
            
            logger.info(f"Successfully fetched {len(formatted_products)} products for location {location_id}")
            
            return Response({
                'success': True,
                'message': 'Products retrieved successfully',
                'data': formatted_products,
                'metadata': {
                    'cached': False,
                    'fetched_at': datetime.now().isoformat(),
                    'location_id': location_id,
                    'location_name': location.location_name,
                    'product_count': len(formatted_products),
                    'product_category': product_category,
                    'cache_expires_in': f"{self.CACHE_TIMEOUT} seconds"
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching Roller products: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _fetch_roller_products(self, api_token, product_category=None):
        """
        Fetch products from Roller API
        
        Args:
            api_token: Roller API access token
            product_category: Optional category filter
        
        Returns:
            List of products or None if failed
        """
        url = "https://api.haveablast.roller.app/products"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        
        params = {}
        if product_category:
            params['ProductCategory'] = product_category
        
        try:
            logger.info(f"Fetching products from Roller API (category: {product_category})")
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            logger.info(f"Roller products API response status: {response.status_code}")
            
            if response.status_code == 200:
                products = response.json()
                logger.info(f"Received {len(products)} products from Roller API")
                return products
            else:
                logger.error(f"Roller API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching products from Roller API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing Roller products response: {str(e)}")
            return None
    
    def _format_products(self, products, location_id):
        """
        Format products to a cleaner structure
        
        Args:
            products: Raw products from Roller API
            location_id: Location ID for reference
        
        Returns:
            Formatted list of products
        """
        formatted_products = []
        
        for product in products:
            try:
                # Extract main product info
                parent_product = {
                    'parent_product_id': product.get('parentProductId'),
                    'parent_product_name': product.get('parentProductName'),
                    'type': product.get('type'),
                    'short_description': product.get('shortDescription', ''),
                    'description': product.get('description', ''),
                    'image_url': product.get('imageurl'),
                    'min_purchase': product.get('minPurchase', 1),
                    'deposit_percentage': product.get('depositPercentage'),
                    'deposit_amount': product.get('depositAmount'),
                    'is_suspended': product.get('isSuspended', False),
                    'tags': product.get('tags', []),
                    'product_category_ids': product.get('productCategoryIds', []),
                    'duration': product.get('duration'),
                    'duration_type': product.get('durationType'),
                    'party_details': product.get('partyDetails'),
                    'is_waiver_required': product.get('isWaiverRequired', False),
                    'capture_ticket_holder_name': product.get('captureTicketHolderName', False),
                    'agreement': product.get('agreement'),
                    # Legacy fields (deprecated but might be useful)
                    'id': product.get('id'),
                    'name': product.get('name'),
                }
                
                # Process product variations
                variations = []
                for variation in product.get('products', []):
                    variation_data = {
                        'id': variation.get('id'),
                        'name': variation.get('name'),
                        'description': variation.get('description', ''),
                        'image_url': variation.get('imageurl'),
                        'price': variation.get('price'),
                        'cost_of_goods': variation.get('costOfGoods'),
                        'tax': variation.get('tax'),
                        'tax_id': variation.get('taxId'),
                        'fee': variation.get('fee'),
                        'group_size': variation.get('groupSize', 1),
                        'is_tax_inclusive': variation.get('isTaxInclusive', False),
                        'min_purchase': variation.get('minPurchase', 1),
                        'max_purchase': variation.get('maxPurchase'),
                        'force_min_purchase': variation.get('forceMinPurchase', False),
                        'has_user_defined_cost': variation.get('hasUserDefinedCost', False),
                        'min_user_defined_cost': variation.get('minUserDefinedCost'),
                        'max_user_defined_cost': variation.get('maxUserDefinedCost'),
                        'is_suspended': variation.get('isSuspended', False),
                        'barcode_id': variation.get('barcodeId'),
                        'par_level': variation.get('parLevel'),
                        'cost': variation.get('cost'),  # deprecated
                        'locations': variation.get('locations', []),
                        'location_times': variation.get('locationTimes', []),
                        'package_items': variation.get('packageItems', []),
                        'package_pricing_type': variation.get('packagePricingType'),
                        'recurring_payment': variation.get('recurringPayment'),
                        'session_discounts': variation.get('sessionDiscounts', []),
                    }
                    
                    # Add product category IDs if available
                    variation_data['product_category_ids'] = variation.get('productCategoryIds', [])
                    
                    variations.append(variation_data)
                
                parent_product['variations'] = variations
                
                # Add package details if it's a package
                if product.get('packageItems'):
                    parent_product['package_items'] = product.get('packageItems')
                
                # Add add-ons if available
                if product.get('addOns'):
                    parent_product['add_ons'] = product.get('addOns')
                
                # Add modifiers if available
                if product.get('modifiers'):
                    parent_product['modifiers'] = product.get('modifiers')
                
                # Add modifier groups if available
                if product.get('modifierGroups'):
                    parent_product['modifier_groups'] = product.get('modifierGroups')
                
                # Add form IDs if available
                if product.get('formIds'):
                    parent_product['form_ids'] = product.get('formIds')
                
                # Add meta data
                parent_product['meta'] = product.get('meta', {})
                
                formatted_products.append(parent_product)
                
            except Exception as e:
                logger.warning(f"Error formatting product {product.get('parentProductId')}: {str(e)}")
                # Continue with other products even if one fails
        
        return formatted_products


class RollerProductCategoriesAPI(APIView):
    """
    API to get available product categories for a location
    
    Note: This extracts categories from products since Roller doesn't have a dedicated categories endpoint
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Get unique product categories for a location
        
        Query Parameters:
        - location_id (required): ID of the location
        """
        try:
            location_id = request.query_params.get('location_id')
            
            if not location_id:
                return Response({
                    'success': False,
                    'message': 'location_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # First get products
            products_api = RollerProductsAPI()
            products_response = products_api._fetch_roller_products_for_categories(location_id)
            
            if not products_response:
                return Response({
                    'success': False,
                    'message': 'Failed to fetch products for categories'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Extract unique categories
            categories = set()
            for product in products_response:
                # Add from productCategoryIds if available
                for cat_id in product.get('productCategoryIds', []):
                    categories.add(cat_id)
                
                # Also check variations
                for variation in product.get('products', []):
                    for cat_id in variation.get('productCategoryIds', []):
                        categories.add(cat_id)
            
            return Response({
                'success': True,
                'message': 'Categories retrieved successfully',
                'data': {
                    'categories': list(categories),
                    'category_count': len(categories),
                    'location_id': location_id
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching product categories: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _fetch_roller_products_for_categories(self, location_id):
        """Helper method to fetch products for category extraction"""
        try:
            location = Location.objects.get(location_id=location_id)
            roller_token = get_or_refresh_roller_token(location)
            print("This is roller token:", roller_token)
            
            if not roller_token:
                return None
            
            url = "https://api.haveablast.roller.app/products"
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {roller_token}"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Error in _fetch_roller_products_for_categories: {str(e)}")
            return None


class RollerProductDetailAPI(APIView):
    """
    API to get details of a specific product by ID
    
    GET /api/roller-product-detail/?location_id=<id>&product_id=<id>
    """
    permission_classes = [AllowAny]
    
    CACHE_TIMEOUT = 86400  # 24 hours
    
    def get(self, request):
        """
        Get detailed information about a specific product
        
        Query Parameters:
        - location_id (required): ID of the location
        - product_id (required): ID of the product (parent product ID)
        """
        try:
            location_id = request.query_params.get('location_id')
            product_id = request.query_params.get('product_id')
            
            if not location_id:
                return Response({
                    'success': False,
                    'message': 'location_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not product_id:
                return Response({
                    'success': False,
                    'message': 'product_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check cache
            cache_key = f"roller_product_detail_{location_id}_{product_id}"
            cached_product = cache.get(cache_key)
            
            if cached_product:
                logger.info(f"Returning cached product detail for product {product_id}")
                return Response({
                    'success': True,
                    'message': 'Product detail retrieved from cache',
                    'data': cached_product,
                    'metadata': {
                        'cached': True,
                        'product_id': product_id,
                        'location_id': location_id
                    }
                })
            
            # Get location and token
            try:
                location = Location.objects.get(location_id=location_id)
            except Location.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'Location with ID {location_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            roller_token = get_or_refresh_roller_token(location)
            print("This is roller token:", roller_token)
            if not roller_token:
                return Response({
                    'success': False,
                    'message': 'Failed to authenticate with Roller API'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Fetch all products and filter
            products = self._fetch_all_products(roller_token)
            if products is None:
                return Response({
                    'success': False,
                    'message': 'Failed to fetch products from Roller API'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Find the specific product
            product_detail = None
            for product in products:
                if (product.get('parentProductId') == product_id or 
                    product.get('id') == product_id):
                    product_detail = product
                    break
            
            if not product_detail:
                return Response({
                    'success': False,
                    'message': f'Product with ID {product_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Cache the product detail
            cache.set(cache_key, product_detail, self.CACHE_TIMEOUT)
            
            return Response({
                'success': True,
                'message': 'Product detail retrieved successfully',
                'data': product_detail,
                'metadata': {
                    'cached': False,
                    'product_id': product_id,
                    'location_id': location_id,
                    'product_name': product_detail.get('parentProductName') or product_detail.get('name')
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching product detail: {str(e)}")
            return Response({
                'success': False,
                'message': 'Internal server error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _fetch_all_products(self, api_token):
        """Fetch all products from Roller API"""
        url = "https://api.haveablast.roller.app/products"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error fetching all products: {str(e)}")
            return None


