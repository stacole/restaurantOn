from gc import get_objects
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from .context_processors import get_cart_counter, get_cart_amounts
from menu.models import FoodItem, MenuRestaurant
from django.shortcuts import redirect

from vendor.models import OpeningHour, Vendor
from django.db.models import Prefetch
from .models import Cart
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance
from datetime import date, datetime

# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    menus = MenuRestaurant.objects.filter(vendor=vendor)
    # menus = MenuRestaurant.objects.filter(vendor=vendor).prefetch_related(
    #     Prefetch(
    #         'fooditems',
    #         queryset = FoodItem.objects.filter(is_available=True)
    #     )
    # )
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')
    # Agregando horario actual abierto.
    today_date = date.today()
    today = today_date.isoweekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day = today)
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor':vendor,
        'menus': menus,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
    }
    return render(request, 'marketplace/vendor_detail.html', context)

def add_to_cart(request, menu_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Verificando si el  menu existe.
            try:
                menu = MenuRestaurant.objects.get(id=menu_id)
                # Checando si el usuario agrego el menu al carrito
                try:
                    chkCart = Cart.objects.get(user=request.user, menu=menu)
                    # Incrementando la cantidad en carrito
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, menu=menu, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the menu tu the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This menu does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalide reques!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

def decrease_cart(request, menu_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Verificando si el  menu existe.
            try:
                menu = MenuRestaurant.objects.get(id=menu_id)
                # Checando si el usuario agrego el menu al carrito
                try:
                    chkCart = Cart.objects.get(user=request.user, menu=menu)
                    if chkCart.quantity > 1:
                        # Restando la cantidad en carrito
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status': 'Success', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this menu in your cart!'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This menu does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalide reques!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

@login_required(login_url = 'login')
def cart(request):
    cart_menus = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_menus': cart_menus,
    }
    return render(request, 'marketplace/cart.html', context)

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # Verificar si existen menus en el carrito
                cart_menu = Cart.objects.get(user=request.user, id=cart_id)
                if cart_menu:
                    cart_menu.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart menu has been deleted!', 'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'Cart menu does not exist!'})    
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalide reques!'})

def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        # templates/home name location
        address = request.GET['address'] 
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

        # tener el restaurante=vendr ids si un usuario lo esta buscando.
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword).values_list('vendor', flat=True)
        
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
            vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
                user_profile__location__distance_lte=(pnt, D(km=radius))
                ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

            for v in vendors:
                v.kms = round(v.distance.km, 1) # en vendors si se cambia distance, cambiar aqui tambien.

            

        vendor_count = vendors.count()
        context = {
            'vendors': vendors,
            'vendor_count': vendor_count,
            'source_location': address,
        }
        
        return render(request, 'marketplace/listings.html', context)