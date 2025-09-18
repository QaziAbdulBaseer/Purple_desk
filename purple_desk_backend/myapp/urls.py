from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from myapp.views import View_Authorization
from myapp.views import View_Locations
from myapp.views import View_hours_of_operations
from myapp.views import View_birthday_party_packages

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

]