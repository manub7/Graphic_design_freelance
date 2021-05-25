from django.shortcuts import render, get_object_or_404, redirect, reverse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .models import DesignRequest, Category
from profiles.models import Client
from profiles.forms import ClientForm
from .forms import OrderFormDesignRequest, OrderFormCheckOut, OrderFormDesignRequestSuser
from orders.models import Order

import stripe
import json




# def design_requests(request, item_id):
# """ A view that renders the design requests page """
# return render(request, 'design_requests/design_requests.html', context )

# A view to create, calculate and capture a design request

def design_request_list(request):
    """ A view to return the index page and show  images  """
    
    client = get_object_or_404(Client, user=request.user)
    design_requests = DesignRequest.objects.all()
    orders = Order.objects.all()
    orders = client.orders.all()

    if request.user.is_authenticated:
        if request.user.is_superuser:
            orders = Order.objects.all()
        else: 
            orders = client.orders.all()
            
  

    context = {
        'orders': orders,
        "design_requests": design_requests,
    }
    return render(request, 'design_requests/design_request_list.html', context)

def design_request_list_uncompleted(request):
    """ A view to return the uncompleted design requests list """
 
    if request.user.is_authenticated:
        client = get_object_or_404(Client, user=request.user)
        if request.user.is_superuser:
            design_requests = DesignRequest.objects.filter(order_number__exact='')
        else: 
            design_requests = DesignRequest.objects.filter(order_number__exact='', client = client)

    context = {
        'design_requests': design_requests,
    }

    return render(request, 'design_requests/design_request_list_uncompleted.html', context)

def add_design_requests(request):

    client = Client.objects.get(user=request.user)
    categories = Category.objects.all()
    if request.method == 'POST':
        form = OrderFormDesignRequest(request.POST, request.FILES)

        if form.is_valid():
            design_request = form.save()
            design_request.client = client
            design_request.save()
            messages.success(request, f'Successfully added the design request: "{design_request.name}" to the list!')
            return redirect(reverse('design_request_checkout', args=[design_request.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = OrderFormDesignRequest()

    context = {
        'form': form,
        'categories': categories,
        'price_factor':settings.PRICE_FACTOR,
    }

    return render(request, 'design_requests/design_requests.html', context)

def update_design_request(request, design_request_id):

    design_request = get_object_or_404(DesignRequest, pk=design_request_id)
    design_request_id = design_request_id
  

    if request.method == 'POST':
        design_request_form = OrderFormDesignRequest(request.POST, request.FILES)

        if design_request_form.is_valid:
            design_request = design_request_form.save()
            design_request.save()
            messages.success(request,f'Successfully updated the  product!')
            return redirect(reverse('design_request_detail', args=[design_request.id]))
        else:
            messages.error(request,f'Failed to add product. Please ensure the form is valid.')

    else:
        design_request_form =  OrderFormDesignRequest(instance=design_request)
    

    context = {
        'design_request_form': design_request_form,
        'design_request_id':design_request_id,
    }
    return render(request,'design_requests/update_design_request.html', context)


def delete_design_request(request, design_request_id):
    
    client = get_object_or_404(Client, user=request.user)
    design_request = get_object_or_404(DesignRequest, pk=design_request_id)
    design_requests = DesignRequest.objects.all()
    orders = Order.objects.all()
    orders = client.orders.all()
    template = 'design_requests/design_request_list.html'
    context = {
        'orders': orders,
        "design_requests": design_requests,
    }
    if request.user.is_authenticated:
        if request.user.is_superuser:
            orders = Order.objects.all()
        else: 
            orders = client.orders.all()

    if  design_request.order_number:
        messages.error(request, 'Sorry, only site owners can do that.')
        return render(request,template, context)
        
    else:
        design_request.delete()
        messages.warning(request, f'Your design request was successfuly deleted')
        return render(request,template, context)


def design_request_detail(request, design_request_id):

    design_request = get_object_or_404(DesignRequest, pk=design_request_id)
    design_request_form =  OrderFormDesignRequest(instance=design_request)

    context = {
        'design_request_form': design_request_form,
        'design_request':design_request,
        'from_design_request_list':True,
    }
    return render(request, 'design_requests/design_request_detail.html', context)
    


def design_request_detail_from_profile(request, design_request_id):

    design_request = get_object_or_404(DesignRequest, pk=design_request_id)
    design_request_id = design_request_id
    design_request_form =  OrderFormDesignRequest(instance=design_request)

    context = {
        'design_request_form': design_request_form,
        'design_request_id':design_request_id,
        'from_profile':True,
    }
    return render(request, 'design_requests/design_request_detail.html', context)



def design_request_process_request(request, design_request_id):

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only site owners can do that.')
        return redirect(reverse('home'))

    design_request = get_object_or_404(DesignRequest, pk=design_request_id)

    if request.method == 'POST':
        design_request_form =  OrderFormDesignRequestSuser(request.POST, request.FILES,instance=design_request)

        if design_request_form.is_valid():
            design_request = design_request_form.save()
            design_request.save()
            messages.success(request, 'Successfully processed the design request processing !')
            return redirect(reverse('design_request_detail', args=[design_request.id]) )
        else:
            messages.error(request, 'Failed to process the deign request. Please ensure the form is valid.')
    else:
        design_request_form = OrderFormDesignRequestSuser(instance=design_request)
        messages.info(request, f'You are processing {design_request.name}')
    
    context = {
        'design_request_form': design_request_form,
        'design_request':design_request,
    }
    return render(request, 'design_requests/design_request_process_request.html', context)


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'design_request_session': json.dumps(request.session.get('form_data', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)



def design_request_checkout(request, design_request_id):

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    print(request.session.get('design_request_session'))
    orders = Order.objects.all()

    if request.user.is_authenticated:
        client = Client.objects.get(user=request.user)
    else:
        messages.error(request, f'Sorry you must log in or register first ')

    design_request = get_object_or_404(DesignRequest, pk=design_request_id)
    order_match = Order.objects.filter(design_request = design_request)

    
    if request.method == "POST":
        if order_match and design_request.order_number:
            messages.error(request, f'You have already ordered this design request ')
        else:
            
            form_data = {
                'first_name': request.POST['first_name'],
                'last_name' : request.POST['last_name'],
                'phone_number': request.POST['phone_number'],
                'country': request.POST.get('country'),
                'postcode': request.POST['postcode'],
                'town_or_city': request.POST['town_or_city'],
                'street_address1': request.POST['street_address1'],
                'street_address2': request.POST['street_address2'],
                'county': request.POST['county'],
            }

            order_form = OrderFormCheckOut(form_data)
            if order_form.is_valid():
                order = order_form.save(commit=False)
                order.design_request = design_request
                order.client = client
                order.price = design_request.price
                pid = request.POST.get('client_secret').split('_secret')[0]
                order.stripe_pid = pid
                order.save()
                # Pass the order number to design request instance 
                design_request.order_number = order.order_number
                design_request.save()
                
                request.session['form_data'] = order_form.cleaned_data 
                request.session['form_data'].update({'design_request_id':'{design_request.id}' })
                print(request.session['form_data'])

                # Save the info to the user's profile if all is well
                id_save_info = False if request.POST.get('#id-save-info') == None  else True,
                if id_save_info:
                    request.session['save_info'] = 'save-info' in request.POST

                messages.success(request, f'Order successfully processed! \
                                            Your order number is {order.order_number}. A confirmation \
                                            email will be sent to {order.client.user.email}.')
                return redirect(reverse('design_request_checkout_success', args=[order.order_number]))
            else:
                messages.error(request, f'There was an error with your form. \
                    Please double check your information.')

    else:
        
        stripe.api_key = stripe_secret_key
        stripe_price =round(design_request.price * 100)
        intent = stripe.PaymentIntent.create(
                    amount=stripe_price,
                    currency=settings.STRIPE_CURRENCY,
                )

        # Attempt to prefill the form with any info the user maintains in their profile
        if request.user.is_authenticated:
            try:
                client = Client.objects.get(user=request.user)
                order_form = OrderFormCheckOut(initial={
                    'first_name': client.default_first_name,
                    'last_name': client.default_last_name,
                    'phone_number': client.default_phone_number,
                    'country': client.default_country,
                    'postcode': client.default_postcode,
                    'town_or_city': client.default_town_or_city,
                    'street_address1': client.default_street_address1,
                    'street_address2': client.default_street_address2,
                    'county': client.default_county,
                })
            except Client.DoesNotExist:
                order_form = OrderFormCheckOut()
                
        else:
            messages.error(request, f'Sorry you must log in or register first ')
    
    if not stripe_public_key:
        messages.warning(request, f'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    order_form = OrderFormCheckOut()
 

    context = {
        
        'stripe_price':stripe_price/100,
        'design_request': design_request,
        'order_form': order_form,
        'stripe_public_key':stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, 'design_requests/design_request_checkout.html', context)

def design_request_checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        client = Client.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.client = client
        order.save()

        # Save the user's info
        if save_info:
            profile_data = {
                'default_first_name':order.first_name,
                'default_last_name':order.last_name,
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }

            client_form = ClientForm(profile_data, instance=client)
            if client_form.is_valid():
                client_form.save()
                messages.success(request, f'Your profile info was updated \
                    with the information provided for your order.')

    if 'save-info' in request.session:
        del request.session['save-info']

    template = 'design_requests/design_request_checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)

def design_request_testimonial (request, design_request_id):

    design_request = get_object_or_404(DesignRequest, pk=design_request_id)
    if request.method == 'POST':
        design_request_form =  OrderFormDesignRequestSuser(request.POST, request.FILES,instance=design_request)

        if design_request_form.is_valid():
            design_request = design_request_form.save()       
            design_request.save()
            messages.success(request, 'Thank you for your testimaonial ! Successfully added the testimonial !')
            return redirect(reverse('design_request_detail', args=[design_request.id]) )
        else:
            messages.error(request, 'Failed to add the testimonial. Please ensure the form is valid.')
    else:
        design_request_form = OrderFormDesignRequestSuser(instance=design_request)

        context = {
        'design_request_form': design_request_form,
        'design_request_id':design_request_id,
    }
    return render(request, 'design_requests/design_request_testimonial.html', context)

