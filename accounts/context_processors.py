from vendor.models import Vendor

def get_vendor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        # Esto es por si no hay un usuario logeado no de error.
        vendor = None
    return dict(vendor=vendor)