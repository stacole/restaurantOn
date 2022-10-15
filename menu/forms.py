from django import forms

from accounts.validators import allow_only_images_validator
from .models import MenuRestaurant, FoodItem

class MenuForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}), validators=[allow_only_images_validator])
    class Meta:
        model = MenuRestaurant
        fields = ['menu_name', 'price', 'description', 'image', 'is_available']

# class FoodItemForm(forms.ModelForm):
#     image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}), validators=[allow_only_images_validator])
#     class Meta:
#         model = FoodItem
#         fields = ['menu_name', 'food_title', 'description', 'image']

