# # from django.contrib import admin

# # # Register your models here.
# # from django.contrib.auth.admin import UserAdmin
# # from .models import User



# # @admin.register(User)
# # class CustomUserAdmin(UserAdmin):
# #     fieldsets = UserAdmin.fieldsets + (
# #         (None, {'fields': ('role',)}),
# #     )



# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User

# # Your custom User admin
# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('role',)}),
#     )

# # API Key admin
# from rest_framework_api_key.models import APIKey
# from rest_framework_api_key.admin import APIKeyModelAdmin

# admin.site.register(APIKey, APIKeyModelAdmin)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
