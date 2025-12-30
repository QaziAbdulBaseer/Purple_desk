

from django.urls import path
from myapp.views import View_FAQs
from myapp.views import View_Policies
from myapp.views import View_Locations
from myapp.views import View_Promotions
from myapp.views import View_membership
from myapp.views import View_Get_Prompt
from myapp.views import View_jump_passes
from myapp.views import View_Authorization
from myapp.views import View_group_booking
from myapp.views import View_ItemsFoodDrinks
from myapp.views import View_rental_facility
from myapp.views import View_hours_of_operations
from myapp.views import View_balloon_party_packages
from myapp.views import View_birthday_party_packages
from rest_framework_simplejwt.views import TokenRefreshView
from myapp.views.Individual_Prompts.create_individual_prompts import (
    create_starting_guidelines_prompt,
    create_current_time_info_prompt,
    create_current_date_prompt,
    create_current_time_prompt,
    create_birthday_party_prompt,
    create_jump_pass_flow_prompt_api,
    create_jump_pass_info_prompt,
    create_membership_flow_prompt_api,
    create_membership_info_prompt,
    create_hours_of_operation_prompt,
    create_faqs_prompt,
    create_policies_prompt,
    create_rental_facility_prompt,
    create_location_info_prompt_api,
    create_prompt_variables_prompt,
    get_combined_all_prompts,
    create_all_prompts_at_once,
    get_location_folder_info
)
# from myapp.utils.prompt_file_utils import combine_all_prompts


# from myapp.views.View_Roller_API.View_Product_Availability import ProductAvailabilityAPIView
from myapp.views.View_Roller_API.View_Product_Availability import ProductAvailabilityAPIView


urlpatterns = [
    ## Authorization Paths
    path('signup/', View_Authorization.register_view, name='signup'),
    path('login/', View_Authorization.token_obtain_pair_view, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', View_Authorization.profile_view, name='profile'),
    path('users/', View_Authorization.user_list, name='user-list'),

    ## Location End points
    path('locations/', View_Locations.get_locations, name='get_locations'),
    path('locations/<int:pk>/', View_Locations.get_location, name='get_location'),
    path('locations/create/', View_Locations.create_location, name='create_location'),
    path('locations/update/<int:pk>/', View_Locations.update_location, name='update_location'),
    path('locations/delete/<int:pk>/', View_Locations.delete_location, name='delete_location'),

    ## Hours operations End points
    path("hours/<int:location_id>/", View_hours_of_operations.get_hours_of_operations, name="get_hours_of_operations"),
    path("hours/<int:location_id>/create/", View_hours_of_operations.create_hours_of_operation, name="create_hours_of_operation"),
    path("hours/<int:location_id>/<int:pk>/update/", View_hours_of_operations.update_hours_of_operation, name="update_hours_of_operation"),
    path("hours/<int:location_id>/<int:pk>/delete/", View_hours_of_operations.delete_hours_of_operation, name="delete_hours_of_operation"),
    
    ## Birthday party packaged end points 
    path("birthday-packages/<int:location_id>/list/", View_birthday_party_packages.get_birthday_party_packages, name="get_birthday_party_packages"),
    path("birthday-packages/<int:location_id>/create/", View_birthday_party_packages.create_birthday_party_package, name="create_birthday_party_package"),
    path("birthday-packages/<int:location_id>/<int:pk>/list/", View_birthday_party_packages.get_birthday_party_package, name="get_birthday_party_package"),
    path("birthday-packages/<int:location_id>/<int:pk>/update/", View_birthday_party_packages.update_birthday_party_package, name="update_birthday_party_package"),
    path("birthday-packages/<int:location_id>/<int:pk>/delete/", View_birthday_party_packages.delete_birthday_party_package, name="delete_birthday_party_package"),
    
    ## Jump passes end points
    path("jump-passes/<int:location_id>/", View_jump_passes.get_jump_passes, name="get_jump_passes"),
    path("jump-passes/<int:location_id>/<int:pk>/", View_jump_passes.get_jump_pass, name="get_jump_pass"),
    path("jump-passes/<int:location_id>/create/", View_jump_passes.create_jump_pass, name="create_jump_pass"),
    path("jump-passes/<int:location_id>/<int:pk>/update/", View_jump_passes.update_jump_pass, name="update_jump_pass"),
    path("jump-passes/<int:location_id>/<int:pk>/delete/", View_jump_passes.delete_jump_pass, name="delete_jump_pass"),

    ## Memberships end points
    path('locations/<int:location_id>/memberships/', View_membership.get_memberships, name='get_memberships'),
    path('locations/<int:location_id>/memberships/create/', View_membership.create_membership, name='create_membership'),
    path('locations/<int:location_id>/memberships/<int:pk>/', View_membership.get_membership, name='get_membership'),
    path('locations/<int:location_id>/memberships/<int:pk>/update/', View_membership.update_membership, name='update_membership'),
    path('locations/<int:location_id>/memberships/<int:pk>/delete/', View_membership.delete_membership, name='delete_membership'),

    ## Balloon Party Packages URLs
    path('balloon-packages/<int:location_id>/', View_balloon_party_packages.get_balloon_party_packages, name='get_balloon_party_packages'),
    path('balloon-packages/<int:location_id>/create/', View_balloon_party_packages.create_balloon_party_package, name='create_balloon_party_package'),
    path('balloon-packages/<int:location_id>/<int:pk>/', View_balloon_party_packages.get_balloon_party_package, name='get_balloon_party_package'),
    path('balloon-packages/<int:location_id>/<int:pk>/update/', View_balloon_party_packages.update_balloon_party_package, name='update_balloon_party_package'),
    path('balloon-packages/<int:location_id>/<int:pk>/delete/', View_balloon_party_packages.delete_balloon_party_package, name='delete_balloon_party_package'),

    ## FAQs End points
    path('locations/<int:location_id>/faqs/', View_FAQs.get_faqs, name='get_faqs'),
    path('locations/<int:location_id>/faqs/create/', View_FAQs.create_faq, name='create_faq'),
    path('locations/<int:location_id>/faqs/<int:pk>/', View_FAQs.get_faq, name='get_faq'),
    path('locations/<int:location_id>/faqs/<int:pk>/update/', View_FAQs.update_faq, name='update_faq'),
    path('locations/<int:location_id>/faqs/<int:pk>/delete/', View_FAQs.delete_faq, name='delete_faq'),
    path('locations/<int:location_id>/faqs/bulk-create/', View_FAQs.bulk_create_faqs, name='bulk_create_faqs'),

    ## Policies End points
    path('locations/<int:location_id>/policies/', View_Policies.get_policies, name='get_policies'),
    path('locations/<int:location_id>/policies/create/', View_Policies.create_policy, name='create_policy'),
    path('locations/<int:location_id>/policies/<int:pk>/', View_Policies.get_policy, name='get_policy'),
    path('locations/<int:location_id>/policies/<int:pk>/update/', View_Policies.update_policy, name='update_policy'),
    path('locations/<int:location_id>/policies/<int:pk>/delete/', View_Policies.delete_policy, name='delete_policy'),
    path('locations/<int:location_id>/policies/bulk-create/', View_Policies.bulk_create_policies, name='bulk_create_policies'),
    path('locations/<int:location_id>/policies/types/', View_Policies.get_policy_types, name='get_policy_types'),

    ## Promotions End points
    path('locations/<int:location_id>/promotions/', View_Promotions.get_promotions, name='get_promotions'),
    path('locations/<int:location_id>/promotions/active/', View_Promotions.get_active_promotions, name='get_active_promotions'),
    path('locations/<int:location_id>/promotions/create/', View_Promotions.create_promotion, name='create_promotion'),
    path('locations/<int:location_id>/promotions/<int:pk>/', View_Promotions.get_promotion, name='get_promotion'),
    path('locations/<int:location_id>/promotions/<int:pk>/update/', View_Promotions.update_promotion, name='update_promotion'),
    path('locations/<int:location_id>/promotions/<int:pk>/delete/', View_Promotions.delete_promotion, name='delete_promotion'),
    path('locations/<int:location_id>/promotions/bulk-create/', View_Promotions.bulk_create_promotions, name='bulk_create_promotions'),
    path('locations/<int:location_id>/promotions/categories/', View_Promotions.get_promotion_categories, name='get_promotion_categories'),

    ## Food/Drink Items endpoints
    path('locations/<int:location_id>/food-drink-items/',View_ItemsFoodDrinks.get_food_drink_items, name='get_food_drink_items'),
    path('locations/<int:location_id>/food-drink-items/categories/',View_ItemsFoodDrinks.get_food_drink_items_by_category, name='get_food_drink_items_by_category'),
    path('locations/<int:location_id>/food-drink-items/categories-list/',View_ItemsFoodDrinks.get_food_drink_categories, name='get_food_drink_categories'),
    path('locations/<int:location_id>/food-drink-items/party-package/',View_ItemsFoodDrinks.get_party_package_items, name='get_party_package_items'),
    path('locations/<int:location_id>/food-drink-items/create/',View_ItemsFoodDrinks.create_food_drink_item, name='create_food_drink_item'),
    path('locations/<int:location_id>/food-drink-items/bulk-create/',View_ItemsFoodDrinks.bulk_create_food_drink_items, name='bulk_create_food_drink_items'),
    path('locations/<int:location_id>/food-drink-items/<int:pk>/',View_ItemsFoodDrinks.get_food_drink_item, name='get_food_drink_item'),
    path('locations/<int:location_id>/food-drink-items/<int:pk>/update/',View_ItemsFoodDrinks.update_food_drink_item, name='update_food_drink_item'),
    path('locations/<int:location_id>/food-drink-items/<int:pk>/delete/',View_ItemsFoodDrinks.delete_food_drink_item, name='delete_food_drink_item'),


 
    ## Rental Facility End points
    path('locations/<int:location_id>/rental-facilities/', View_rental_facility.get_rental_facilities, name='get_rental_facilities'),
    path('locations/<int:location_id>/rental-facilities/create/', View_rental_facility.create_rental_facility, name='create_rental_facility'),
    path('locations/<int:location_id>/rental-facilities/<int:pk>/', View_rental_facility.get_rental_facility, name='get_rental_facility'),
    path('locations/<int:location_id>/rental-facilities/<int:pk>/update/', View_rental_facility.update_rental_facility, name='update_rental_facility'),
    path('locations/<int:location_id>/rental-facilities/<int:pk>/delete/', View_rental_facility.delete_rental_facility, name='delete_rental_facility'),
    path('locations/<int:location_id>/rental-facilities/bulk-create/', View_rental_facility.bulk_create_rental_facilities, name='bulk_create_rental_facilities'),


 
    ## Group Booking End points
    path('locations/<int:location_id>/group-bookings/', View_group_booking.get_group_bookings, name='get_group_bookings'),
    path('locations/<int:location_id>/group-bookings/create/', View_group_booking.create_group_booking, name='create_group_booking'),
    path('locations/<int:location_id>/group-bookings/<int:pk>/', View_group_booking.get_group_booking, name='get_group_booking'),
    path('locations/<int:location_id>/group-bookings/<int:pk>/update/', View_group_booking.update_group_booking, name='update_group_booking'),
    path('locations/<int:location_id>/group-bookings/<int:pk>/delete/', View_group_booking.delete_group_booking, name='delete_group_booking'),
    path('locations/<int:location_id>/group-bookings/bulk-create/', View_group_booking.bulk_create_group_bookings, name='bulk_create_group_bookings'),



    # Your existing endpoints
    path("get-prompt/<int:location_id>/<int:search_number>/<int:client_id>", View_Get_Prompt.get_prompt, name="View_Get_Prompt"),
    


    # System prompts
    path("create-starting-guidelines/", create_starting_guidelines_prompt, name="create_starting_guidelines"),
    path("create-current-time-info/<str:timezone>", create_current_time_info_prompt, name="create_current_time_info"),
    
    # Location-specific prompts
    path("create-current-date/<int:location_id>", create_current_date_prompt, name="create_current_date"),
    path("create-current-time/<int:location_id>", create_current_time_prompt, name="create_current_time"),
    path("create-birthday-prompt/<int:location_id>/<int:search_number>/<int:client_id>", create_birthday_party_prompt, name="create_birthday_prompt"),
    path("create-jump-pass-flow/<int:location_id>", create_jump_pass_flow_prompt_api, name="create_jump_pass_flow"),
    path("create-jump-pass-info/<int:location_id>", create_jump_pass_info_prompt, name="create_jump_pass_info"),
    path("create-membership-flow/<int:location_id>", create_membership_flow_prompt_api, name="create_membership_flow"),
    path("create-membership-info/<int:location_id>", create_membership_info_prompt, name="create_membership_info"),
    path("create-hours-prompt/<int:location_id>", create_hours_of_operation_prompt, name="create_hours_prompt"),
    path("create-faqs-prompt/<int:location_id>", create_faqs_prompt, name="create_faqs_prompt"),
    path("create-policies-prompt/<int:location_id>", create_policies_prompt, name="create_policies_prompt"),
    path("create-rental-prompt/<int:location_id>", create_rental_facility_prompt, name="create_rental_prompt"),
    path("create-location-info/<int:location_id>", create_location_info_prompt_api, name="create_location_info"),
    path("create-prompt-variables/<int:location_id>", create_prompt_variables_prompt, name="create_prompt_variables"),
    
    # Combined and folder operations
    path("get-combined-all/<int:location_id>", get_combined_all_prompts, name="get_combined_all"),
    path("create-all-prompts/<int:location_id>/<int:search_number>/<int:client_id>", create_all_prompts_at_once, name="create_all_prompts"),
    path("get-folder-info/<int:location_id>", get_location_folder_info, name="get_folder_info"),

    path('product_availability/', ProductAvailabilityAPIView.as_view(), name='product_availability'),


    ## Get Prompt
    # path("get-prompt/<int:location_id>/<int:search_number>/<int:client_id>", View_Get_Prompt.get_prompt, name="View_Get_Prompt"),
] 