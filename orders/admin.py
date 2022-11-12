from django.contrib import admin
from .models import Payment, Order, OrderedMenu

# Register your models here.
# class OrderedMenuInline(admin.TabularInline):
    # model = OrderedMenu
    # Esta lista es de orders.views.payment form menu in cart_menus.
    # readonly_fields = ('order', 'payment', 'user', 'menuitem', 'quantity', 'price', 'amount')
    # extra = 0

class OrderedMenuAdmin(admin.ModelAdmin):
    readonly_fields = ('order', 'payment', 'user', 'menuitem', 'quantity', 'price', 'amount','table', 'bracelet')

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'name', 'phone_number', 'email', 'total', 'payment_method', 'status', 'is_ordered']
    # inlines = [OrderedMenuInline]

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedMenu)