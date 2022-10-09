# from tabnanny import verbose
from django.db import models
from vendor.models import Vendor


class MenuRestaurant(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    menu_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length=250, blank=True)
    image = models.ImageField(upload_to='menuimages')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'menu'
        verbose_name_plural = 'menus'

    def clean(self):
        self.menu_name = self.menu_name.capitalize()
    
    def __str__(self):
        return self.menu_name


class FoodItem(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    # menu = models.ForeignKey(MenuRestaurant, on_delete=models.CASCADE, related_name='fooditems')
    menu = models.ForeignKey(MenuRestaurant, on_delete=models.CASCADE)
    food_title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=250, blank=True)
    image = models.ImageField(upload_to='foodimages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_title