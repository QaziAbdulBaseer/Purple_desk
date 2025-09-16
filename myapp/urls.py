from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from myapp.views import View_Authorization
from myapp.views import View_Locations

urlpatterns = [
    path("get_csrf/", View_Locations.get_csrf, name="get_csrf"),

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
]