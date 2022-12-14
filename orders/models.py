import json

from django.db import models

from accounts.models import User
from menu.models import MenuRestaurant
from vendor.models import Vendor

request_object = ''

class Payment(models.Model):
    # Seleccionar metodo de pago
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id

# class Brazalets(models.Model):
#     number = models.IntegerField()
#     detail = models.CharField(null=True, blank=True)

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    vendors = models.ManyToManyField(Vendor, blank=True, verbose_name="Restaurant")
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10)
    total = models.FloatField()
    tax_data = models.JSONField(blank=True, help_text = "Data format: {'tax_type':{'tax_percentage':'tax_amount'}}", null=True)
    total_data = models.JSONField(blank=True, null=True)
    total_tax = models.FloatField()
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    table = models.IntegerField(blank=True, null=True)
    bracelet = models.CharField(max_length=150, blank=True, null=True)
    #bacelet = models.ForeignKey(Brazalets, blank=True, on_delete=models.CASCADE, null=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Devolver nombre y apellido concatenado.
    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    def restaurant(self):
        return ", ".join([str(i) for i in self.vendors.all()])

    def get_total_by_vendor(self):
        # create custom middleware django documentaci??n
        vendor = Vendor.objects.get(user=request_object.user)
        print(vendor)
        
        subtotal = 0
        tax = 0
        tax_dict = {}
        if self.total_data: # revisar porque no funciona sin el None
            total_data = json.loads(self.total_data)
            print(total_data)
            data = total_data.get(str(vendor.id))
            # print(total_data)
            print(data)
            for key, val in data.items():
                subtotal += float(key)
                val = val.replace("'", '"')
                val = json.loads(val)
                tax_dict.update(val)

                # calcular tax
                # {'iva': {'9.00': '6.03'}, 'paypal': {'7.00': '4.69'}}
                for i in val:
                    for j in val[i]:
                        tax += float(val[i][j])
        grand_total = float(subtotal) + float(tax)
        context = {
            'subtotal': subtotal,
            'tax_dict': tax_dict, 
            'grand_total': grand_total,
        }
        return context

    # def bracelets(self):
    #     bracelet_all = self.bracelet
    #     separate = "-"
    #     bra = " TB"
    #     # splits = "-".join(str(bracelet_all).split(separate))
    #     splits = str(bracelet_all).split(separate)
    #     return bra.join([j for j in splits])

    def __str__(self):
        return self.order_number

class OrderedMenu(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuRestaurant, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        #  str() 
        return self.menuitem.menu_name


