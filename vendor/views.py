from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from menu.forms import MenuForm, FoodItemForm
from orders.models import Order, OrderedMenu
from . forms import VendorForm, OpeningHourForm
from accounts.forms import UserProfileForm

from accounts.models import UserProfile
from .models import OpeningHour, Vendor
from django.contrib import messages

# Metodos para que no de error al querer entrar a la pagina de perfil de Vendor sin estar logueado, redireccione a inicio. 
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor
from menu.models import FoodItem, MenuRestaurant
from django.template.defaultfilters import slugify

# Create your views here.

def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings update.')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, 'vendor/vprofile.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    menus = MenuRestaurant.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'menus': menus,
    }
    return render(request, 'vendor/menu_builder.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_menu(request, pk=None):
    vendor = get_vendor(request)
    menu = get_object_or_404(MenuRestaurant, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, menu=menu)
    context = {
        'fooditems': fooditems,
        'menu': menu,
    }
    return render(request, 'vendor/fooditems_by_menu.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_menu(request):
    if request.method == 'POST':
        form = MenuForm(request.POST, request.FILES) # contiene imagen y requiere esto
        if form.is_valid():
            menu_name = form.cleaned_data['menu_name']
            menu = form.save(commit=False)
            menu.vendor = get_vendor(request)

            menu.save() # here the menu id will be generated
            #form.save()
            menu.slug = slugify(menu_name)+'-'+str(menu.id) # pizza-18
            menu.save()
            messages.success(request, 'Menu added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = MenuForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_menu.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_menu(request, pk=None):
    menu = get_object_or_404(MenuRestaurant, pk=pk)
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            menu_name = form.cleaned_data['menu_name']
            menu = form.save(commit=False)
            menu.vendor = get_vendor(request)

            # menu.save() # here the menu id will be generated
            menu.slug = slugify(menu_name)
            form.save()
            messages.success(request, 'Menu updated successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = MenuForm(instance=menu) # esto rellena el formulario automaticamente para editarlo.
    context = {
        'form': form,
        'menu': menu,
    }
    return render(request, 'vendor/edit_menu.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_menu(request, pk=None):
    menu = get_object_or_404(MenuRestaurant, pk=pk)
    menu.delete()
    messages.success(request, 'Menu has been delete successfully!')
    return redirect('menu_builder')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES) # contiene imagen y requiere esto
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)

            # food.save() # here the food id will be generated
            
            food.save() # here the food id will be generated
            #form.save()
            food.slug = slugify(foodtitle)+'-'+str(food.id) # pizza-18
            food.save()
            messages.success(request, 'Foof Item added successfully!')
            return redirect('fooditems_by_menu', food.menu.id)
        else:
            print(form.errors)
    else:
       form = FoodItemForm()
       # Modificando categorias al agregar food a un menu desde otro usuario.
       form.fields['menu'].queryset = MenuRestaurant.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES,  instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)

            # food.save() # here the food id will be generated
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, 'Food Item updated successfully!')
            return redirect('fooditems_by_menu', food.menu.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm(instance=food) # esto rellena el formulario automaticamente para editarlo.
        # Modificando categorias al agregar food a un menu desde otro usuario.
        form.fields['menu'].queryset = MenuRestaurant.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form,
        'food': food, # Esta instancia se le pasa al form en edit_food.html porque en vendor/urls.py se solicita el primary key en el url
    }
    return render(request, 'vendor/edit_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food Item has been delete successfully!')
    return redirect('fooditems_by_menu', food.menu.id)

def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': opening_hours,
    }
    return render(request, 'vendor/opening_hours.html', context)

def add_opening_hours(request):
    # manejar los datos y despues los  guarda dentro de la base de datos
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method =='POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')

            try:
                hour = OpeningHour.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': hour.to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status': 'failed', 'message': from_hour+'-'+to_hour+' already exists for this day!'}
                return JsonResponse(response)
        else:
            HttpResponse('Invalid requestr')

def remove_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status': 'success', 'id': pk})

def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_menu = OrderedMenu.objects.filter(order=order, menuitem__vendor=get_vendor(request)) #Función get_vendor al principio de esta página
        
        context = {
            'order': order,
            'ordered_menu': ordered_menu,
        }
    except:
        return redirect('vendor')

    return render(request, 'vendor/order_detail.html', context)