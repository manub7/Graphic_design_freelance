from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Client
from orders.models import Order
from .forms import ClientForm

# Create your views here.
@login_required
def profile(request):
    """ Display users's profile  """
    profile = get_object_or_404(Client, user=request.user)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Please make sure the form is valid')
    else:
        form = ClientForm(instance=profile)

    orders = profile.orders.all()
    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders':orders,
    }

    return render(request, template, context)

@login_required
def order_history(request, order_number):
    client = get_object_or_404(Client, user=request.user)
    order = get_object_or_404(Order, order_number=order_number)

    if order.client != client and not request.user.is_superuser:
        messages.error(request, "You don't have permission to do that.")
        return redirect(reverse('profile'))

    template = 'orders/order_detail.html'
    context = {
        'order':order,
        'from_profile':True,
    }

    return render(request,template, context)
