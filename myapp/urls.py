


from django.urls import path
from myapp.views import View_FAQs
from myapp.views import View_Policies
from myapp.views import View_Locations
from myapp.views import View_Promotions
from myapp.views import View_membership
from myapp.views import View_Get_Prompt
from myapp.views import View_jump_passes
from myapp.views import View_Authorization
from myapp.views import View_hours_of_operations
from myapp.views import View_balloon_party_packages
from myapp.views import View_birthday_party_packages
from myapp.views import View_birthday_balloon_bridge
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # path("get_csrf/", View_Locations.get_csrf, name="get_csrf"),
    ## This is the Authorization Paths
    path('signup/', View_Authorization.register_view, name='signup'),
    path('login/', View_Authorization.token_obtain_pair_view, name='login'),     # returns access & refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', View_Authorization.profile_view, name='profile'),           # protected endpoint
    path('users/', View_Authorization.user_list, name='user-list'),

    ## Location End points

    path('locations/', View_Locations.get_locations, name='get_locations'),          # GET all
    path('locations/<int:pk>/', View_Locations.get_location, name='get_location'),   # GET one
    path('locations/create/', View_Locations.create_location, name='create_location'), # POST
    path('locations/update/<int:pk>/', View_Locations.update_location, name='update_location'), # PUT
    path('locations/delete/<int:pk>/', View_Locations.delete_location, name='delete_location'), # DELETE


    ## Hours operations End points

    path("hours/<int:location_id>/", View_hours_of_operations.get_hours_of_operations, name="get_hours_of_operations"),
    path("hours/<int:location_id>/create/", View_hours_of_operations.create_hours_of_operation, name="create_hours_of_operation"),
    path("hours/<int:location_id>/<int:pk>/update/", View_hours_of_operations.update_hours_of_operation, name="update_hours_of_operation"),
    path("hours/<int:location_id>/<int:pk>/delete/", View_hours_of_operations.delete_hours_of_operation, name="delete_hours_of_operation"),

    
    ## birthday party packaged end points 
    path("birthday-packages/<int:location_id>/list/", View_birthday_party_packages.get_birthday_party_packages, name="get_birthday_party_packages"), # Get all
    path("birthday-packages/<int:location_id>/create/", View_birthday_party_packages.create_birthday_party_package, name="create_birthday_party_package"), # Create
    path("birthday-packages/<int:location_id>/<int:pk>/list/", View_birthday_party_packages.get_birthday_party_package, name="get_birthday_party_package"), #get one
    path("birthday-packages/<int:location_id>/<int:pk>/update/", View_birthday_party_packages.update_birthday_party_package, name="update_birthday_party_package"),  # Update
    path("birthday-packages/<int:location_id>/<int:pk>/delete/", View_birthday_party_packages.delete_birthday_party_package, name="delete_birthday_party_package"),  # Delete one
    
    ## jump passes end points
    path("jump-passes/<int:location_id>/", View_jump_passes.get_jump_passes, name="get_jump_passes"), #Get all 
    path("jump-passes/<int:location_id>/<int:pk>/", View_jump_passes.get_jump_pass, name="get_jump_pass"), # Get a specific jump pass
    path("jump-passes/<int:location_id>/create/", View_jump_passes.create_jump_pass, name="create_jump_pass"), # create
    path("jump-passes/<int:location_id>/<int:pk>/update/", View_jump_passes.update_jump_pass, name="update_jump_pass"), # Update
    path("jump-passes/<int:location_id>/<int:pk>/delete/", View_jump_passes.delete_jump_pass, name="delete_jump_pass"), # Delete
 


    ## memberships end points
    path('locations/<int:location_id>/memberships/', View_membership.get_memberships, name='get_memberships'), # GET all memberships for a location
    path('locations/<int:location_id>/memberships/create/', View_membership.create_membership, name='create_membership'), # POST create membership
    path('locations/<int:location_id>/memberships/<int:pk>/', View_membership.get_membership, name='get_membership'), # GET one membership
    path('locations/<int:location_id>/memberships/<int:pk>/update/', View_membership.update_membership, name='update_membership'), # PUT update membership
    path('locations/<int:location_id>/memberships/<int:pk>/delete/', View_membership.delete_membership, name='delete_membership'), # DELETE membership


    # Balloon Party Packages URLs
    path('balloon-packages/<int:location_id>/', View_balloon_party_packages.get_balloon_party_packages, name='get_balloon_party_packages'),
    path('balloon-packages/<int:location_id>/create/', View_balloon_party_packages.create_balloon_party_package, name='create_balloon_party_package'),
    path('balloon-packages/<int:location_id>/<int:pk>/', View_balloon_party_packages.get_balloon_party_package, name='get_balloon_party_package'),
    path('balloon-packages/<int:location_id>/<int:pk>/update/', View_balloon_party_packages.update_balloon_party_package, name='update_balloon_party_package'),
    path('balloon-packages/<int:location_id>/<int:pk>/delete/', View_balloon_party_packages.delete_balloon_party_package, name='delete_balloon_party_package'),
    
    # Birthday-Balloon Bridge URLs
    path('birthday-packages/<int:location_id>/<int:birthday_package_id>/balloons/', View_birthday_balloon_bridge.get_birthday_package_balloons, name='get_birthday_package_balloons'),
    path('birthday-packages/<int:location_id>/<int:birthday_package_id>/balloons/add/', View_birthday_balloon_bridge.add_balloon_to_birthday_package, name='add_balloon_to_birthday_package'),
    path('birthday-packages/<int:location_id>/<int:birthday_package_id>/balloons/<int:balloon_package_id>/remove/', View_birthday_balloon_bridge.remove_balloon_from_birthday_package, name='remove_balloon_from_birthday_package'),


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


    ## Get Prompt
    path("get-prompt/<int:location_id>/", View_Get_Prompt.get_prompt, name="View_Get_Prompt"), # Get


]