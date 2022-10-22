from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'role', 'is_active')
    ordering = ('-date_joinde',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)

# Titulo de la pagina en el portal administrador

admin.site.site_header = "Thompson Hotels"
admin.site.site_title = "Restaurant Administrator"
admin.site.index_title = "Welcome to Admin portal"