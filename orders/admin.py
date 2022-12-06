from django.contrib import admin
from .models import Payment, Order, OrderedMenu
from import_export.admin import ImportExportModelAdmin

# Register your models here.
class OrderedMenuInline(admin.TabularInline):
    model = OrderedMenu
    # Esta lista es de orders.views.payment form menu in cart_menus.
    readonly_fields = ('order', 'payment', 'user', 'menuitem', 'quantity', 'price', 'amount')
    extra = 0

class OrderedMenuAdmin(admin.ModelAdmin):
    readonly_fields = ('order', 'payment', 'user', 'menuitem', 'quantity', 'price', 'amount')

class OrderAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'order_number', 'payment', 'name', 'phone_number', 'email', 'country', 'state', 'city', 'pin_code', 'total', 'payment_method', 'status', 'bracelet', 'table', 'restaurant', 'is_ordered', 'created_at']
    search_fields = ['order_number', 'last_name']
    list_filter = ('vendors', 'status', 'is_ordered')
    # readonly_fields = ['order_number', 'name', 'phone_number', 'email', 'total', 'payment_method', 'status', 'order_placed_to', 'is_ordered']
    inlines = [OrderedMenuInline]
    # list_editable = ['bracelet', 'table']

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedMenu)