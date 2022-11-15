from django.shortcuts import render, redirect
from marketplace.models import Cart, Tax
from marketplace.context_processors import get_cart_amounts
from menu.models import MenuRestaurant
from .forms import OrderForm
from .models import Order, OrderedMenu, Payment
import simplejson as json
from .utils import generate_order_number
from django.http import HttpResponse, JsonResponse
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='login')
def place_order(request):
    cart_menus = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_menus.count()
    if cart_count <= 0:
        return redirect('marketplace')

    vendors_ids = []
    for i in cart_menus:
        if i.menu.vendor.id not in vendors_ids:
            vendors_ids.append(i.menu.vendor.id)
    
    # Esta función es de context_proccessors
    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    k = {}
    for i in cart_menus:
        menu = MenuRestaurant.objects.get(pk=i.menu.id, vendor_id__in=vendors_ids)
        v_id = menu.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (menu.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (menu.price * i.quantity)
            k[v_id] = subtotal

        # Calcular los datos de impuestos
        total_data = {}
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage) : str(tax_amount)}})
        # construct total data
        # {"vendor_id":{"subtotal":{"tax_type": {"tax_percentage": "tax_amount"}}}}
        total_data.update({menu.vendor.id: {str(subtotal): str(tax_dict)}})


        # tax = sum(x for key in tax_dict.values() for x in key.values())

        # grand_total = subtotal + tax

    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone_number = form.cleaned_data['phone_number']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save() # Generación del order id/pk 
            order.order_number = generate_order_number(order.id)
            order.save() # Guarado de order id/pk con la fecha actual.
            order.vendors.add(*vendors_ids)
            context = {
                'order': order,
                'cart_menus': cart_menus,
            }
            return render(request, 'orders/place_order.html', context)

        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')

@login_required(login_url='login')
def payments(request):
    # Compuobar si la solicitud es AJAX o no
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        # Almacenar los datos de pago en MODEL PAYMENT
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
        payment.save()
        # Actualizar MODEL ORDER
        order.payment = payment
        order.is_ordered = True
        order.save()
        # Mover los artículos del carro a MODEL MENU ordenado
        cart_menus = Cart.objects.filter(user=request.user)
        for menu in cart_menus:
            ordered_menu = OrderedMenu()
            ordered_menu.order = order
            ordered_menu.payment = payment
            ordered_menu.user = request.user
            ordered_menu.menuitem = menu.menu
            ordered_menu.quantity = menu.quantity
            ordered_menu.price = menu.menu.price
            ordered_menu.amount = menu.menu.price * menu.quantity # Total amount
            ordered_menu.save()

        # Enviar correo electrónico de confirmación de pedido a CUSTOMER
        mail_subject = 'Thanks for enjoy the best restaurant in Riviera Maya'
        mail_template = 'orders/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
        }
        send_notification(mail_subject, mail_template, context)
        
        # Enviar correo electrónico de pedido recibido a VENDOR
        mail_subject = 'You are received a new order.'
        mail_template = 'orders/new_order_received.html'
        to_emails = []
        for i in cart_menus:
            if i.menu.vendor.user.email not in to_emails: # Condicional para que no se repipta el correo enviado a vendor cuando es mas de una orden
                to_emails.append(i.menu.vendor.user.email) # de marketplace.models.cart {menu} el modelo foreingkey vendor, user
        print('to_emails=>', to_emails)
        context = {
            'order': order,
            'to_email':to_emails
        }
        send_notification(mail_subject, mail_template, context)
        
        # Borrar el carrito si el pago es éxitoso
        cart_menus.delete()

        # Volver a AJAX con éxito o fracaso del estatus

        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
        }
        return JsonResponse(response)
    
    return HttpResponse('Payments view')

def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id') # trans_id es una variable de place_order.html window.location.href = order_complete +

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_menu = OrderedMenu.objects.filter(order=order)

        subtotal = 0
        for menu in ordered_menu:
            subtotal += (menu.price * menu.quantity)

        tax_data = json.loads(order.tax_data)
        #print(tax_data)
        context = {
            'order': order,
            'ordered_menu': ordered_menu,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')