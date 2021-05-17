from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Client
from orders.models import Order
from .forms import ClientForm

# Create your views here.
def profile(request):
    """ Display users's profile  """
    profile = get_object_or_404(Client, user=request.user)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')

    form = ClientForm(instance=profile)
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders':orders,
    }

    return render(request, template, context)

def order_history(request,order_number):
    order= get_object_or_404(Order,order_number=order_number)

    template = 'orders/order_detail.html'
    context = {
        'order':order,
        'from_profile':True,
    }

    return render(request,template, context)