from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'), # vendor_slug vendor.models

    # Agregar al carro
    path('add_to_cart/<int:menu_id>/', views.add_to_cart, name='add_to_cart'),
    # Restando al carrito
    path('decrease_cart/<int:menu_id>/', views.decrease_cart, name='decrease_cart'),
    # Borrado de carro
    path('delete_cart/<int:cat_id>/', views.delete_cart, name='delete_cart'),
]