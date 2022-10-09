from django.contrib import admin
from .models import MenuRestaurant, FoodItem

# Register your models here.
class MenuRestaurantAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('menu_name',)}
    list_display = ('menu_name', 'vendor', 'price', 'is_available', 'updated_at')
    search_fields = ('menu_name', 'vendor__vendor_name', 'price') # vendor__ es para que no de error al buscar, ya que es una llave foranea.
    list_filter = ('is_available',)

class FoodItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('food_title',)}
    list_display = ('food_title', 'menu', 'vendor', 'updated_at')
    search_fields = ('food_title', 'menu__menu_name', 'vendor__vendor_name')

admin.site.register(MenuRestaurant, MenuRestaurantAdmin)
admin.site.register(FoodItem, FoodItemAdmin)