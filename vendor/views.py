from django.shortcuts import get_object_or_404, redirect, render

from menu.forms import MenuForm
from . forms import VendorForm
from accounts.forms import UserProfileForm

from accounts.models import UserProfile
from .models import Vendor
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

#@login_required(login_url='login')
#@user_passes_test(check_role_vendor)
def add_menu(request):
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            menu_name = form.cleaned_data['menu_name']
            menu = form.save(commit=False)
            menu.vendor = get_vendor(request)

            # menu.save() # here the menu id will be generated
            menu.slug = slugify(menu_name)
            form.save()
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

def delete_menu(request, pk=None):
    menu = get_object_or_404(MenuRestaurant, pk=pk)
    menu.delete()
    messages.success(request, 'Menu has been delete successfully!')
    return redirect('menu_builder')