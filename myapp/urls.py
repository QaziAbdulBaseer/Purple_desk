from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from myapp.views import Authorization
from myapp.views import Locations

urlpatterns = [
    ## This is the Authorization Paths
    path('signup/', Authorization.register_view, name='signup'),
    path('login/', Authorization.token_obtain_pair_view, name='login'),     # returns access & refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', Authorization.profile_view, name='profile'),           # protected endpoint
    path('users/', Authorization.user_list, name='user-list'),

    ## Location End points

    path('locations/', Locations.get_locations, name='get_locations'),          # GET all
    path('locations/<int:pk>/', Locations.get_location, name='get_location'),   # GET one
    path('locations/create/', Locations.create_location, name='create_location'), # POST
    path('locations/update/<int:pk>/', Locations.update_location, name='update_location'), # PUT
    path('locations/delete/<int:pk>/', Locations.delete_location, name='delete_location'), # DELETE
]