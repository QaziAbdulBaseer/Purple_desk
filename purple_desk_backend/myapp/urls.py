from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from myapp.views import View_Authorization
from myapp.views import View_Locations
from myapp.views import View_hours_of_operations
from myapp.views import View_birthday_party_packages
from myapp.views import View_jump_passes
from myapp.views import View_Get_Prompt
from myapp.views import View_membership
from myapp.views import View_Balloon_packages
from myapp.views import View_birthday_balloon_association
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

    ## Party Balloon Packages endpoints
    path('locations/<int:location_id>/party_balloon_packages/', View_Balloon_packages.get_party_balloon_packages, name='get_party_balloon_packages'),
    path('locations/<int:location_id>/party_balloon_packages/create/', View_Balloon_packages.create_party_balloon_package, name='create_party_balloon_package'),
    path('locations/<int:location_id>/party_balloon_packages/<int:pk>/', View_Balloon_packages.get_party_balloon_package, name='get_party_balloon_package'),
    path('locations/<int:location_id>/party_balloon_packages/<int:pk>/update/', View_Balloon_packages.update_party_balloon_package, name='update_party_balloon_package'),
    path('locations/<int:location_id>/party_balloon_packages/<int:pk>/delete/', View_Balloon_packages.delete_party_balloon_package, name='delete_party_balloon_package'),


    # Birthday Balloon Association endpoints
    path('locations/<int:location_id>/birthday_packages/<int:birthday_package_id>/available_balloon_packages/', View_birthday_balloon_association.get_available_balloon_packages_for_birthday_package, name='get_available_balloon_packages'),
    path('locations/<int:location_id>/birthday_balloon_associations/', View_birthday_balloon_association.get_birthday_party_balloon_packages, name='get_birthday_balloon_associations'),
    path('locations/<int:location_id>/birthday_balloon_associations/create/', View_birthday_balloon_association.create_birthday_party_balloon_package, name='create_birthday_balloon_association'),
    path('locations/<int:location_id>/birthday_balloon_associations/<int:pk>/', View_birthday_balloon_association.get_birthday_party_balloon_package, name='get_birthday_balloon_association'),
    path('locations/<int:location_id>/birthday_balloon_associations/<int:pk>/update/', View_birthday_balloon_association.update_birthday_party_balloon_package, name='update_birthday_balloon_association'),
    path('locations/<int:location_id>/birthday_balloon_associations/<int:pk>/delete/', View_birthday_balloon_association.delete_birthday_party_balloon_package, name='delete_birthday_balloon_association'),

    # Special endpoints for birthday package associations
    path('locations/<int:location_id>/birthday_packages/<int:birthday_package_id>/balloon_packages/', View_birthday_balloon_association.get_birthday_party_balloon_packages_by_birthday_package, name='get_balloon_packages_by_birthday_package'),
    path('locations/<int:location_id>/birthday_packages/<int:birthday_package_id>/available_balloon_packages/', View_birthday_balloon_association.get_available_balloon_packages_for_birthday_package, name='get_available_balloon_packages_for_birthday_package'),



    ## Get Prompt
    path("get-prompt/<int:location_id>/", View_Get_Prompt.get_prompt, name="View_Get_Prompt"), # Get


]