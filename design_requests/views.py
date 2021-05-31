from django.shortcuts import render, get_object_or_404, redirect, reverse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

from .models import DesignRequest, Category
from profiles.models import Client
from profiles.forms import ClientForm
from .forms import OrderFormDesignRequest, OrderFormCheckOut, OrderFormDesignRequestSuser
from orders.models import Order


import stripe
import json




# Design request views 

@login_required
def design_request_list(request):
    """ A view to return the index page and show  images  """
    processed_requests = 0
    unprocessed_requests = 0
    uncomplete_requests = 0
    uncomplete_requests_bool = False 

    client = get_object_or_404(Client, user=request.user)
    design_requests = DesignRequest.objects.all()
    orders = Order.objects.all()
    orders = client.orders.all()

    if request.user.is_authenticated:
        if request.user.is_superuser:
            orders = Order.objects.all()
        else: 
            orders = client.orders.all()
        for order in orders: 
            if (order.design_request.is_processed):
                processed_requests += 1
            elif (not order.design_request.is_processed) : 
                unprocessed_requests += 1
            else : 
                processed_requests=  processed_requests
                unprocessed_requests = unprocessed_requests
  
        for design_request in design_requests:
            if (not design_request.order_number and not design_request.is_processed ):
                uncomplete_requests += 1
            else:
                uncomplete_requests = uncomplete_requests


    context = {
        'orders': orders,
        'processed_requests': processed_requests,
        'unprocessed_requests':unprocessed_requests,
        'uncomplete_requests':uncomplete_requests,
        "design_requests": design_requests,
       

    }
    return render(request, 'design_requests/design_request_list.html', context)

@login_required
def design_request_unprocessed_list(request):
    """ A view to return the unprocessed design request available only to the superuser  """
    
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only site owners can do that.')
        return redirect(reverse('home'))

    client = get_object_or_404(Client, user=request.user)
    orders = Order.objects.all()
  

    context = {
        'orders': orders,
    }
    return render(request, 'design_requests/design_request_unprocessed_list.html', context)

@login_required
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

@login_required
def add_design_requests(request):
    """ A view to add  design requests and redirect to the design request list """
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

@login_required
def update_design_request(request, design_request_id):
    """ A view to update design requests and redirect to the design request detail """
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

@login_required
def delete_design_request(request, design_request_id):
    """ A view to delete design requests and redirect to the design request list """
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
        return render(request, 'template', context)
    else:
        design_request.delete()
        messages.warning(request, f'Your design request was successfuly deleted')

    return render(request, template, context)


@login_required
def design_request_detail(request, design_request_id):
    """ A view to  design requests details  """
    design_request = get_object_or_404(DesignRequest, pk=design_request_id)
    design_request_form =  OrderFormDesignRequest(instance=design_request)

    context = {
        'design_request_form': design_request_form,
        'design_request':design_request,
        'from_design_request_list':True,
    }
    return render(request, 'design_requests/design_request_detail.html', context)

@login_required
def design_request_testimonial (request, design_request_id):
    """ A view to render and capture the design request testimonial if any """
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

@login_required
def design_request_detail_from_profile(request, design_request_id):
    """ A view for  design requests detail with a button for the profile view  """
    design_request = get_object_or_404(DesignRequest, pk=design_request_id)
    design_request_id = design_request_id
    design_request_form =  OrderFormDesignRequest(instance=design_request)

    context = {
        'design_request_form': design_request_form,
        'design_request_id':design_request_id,
        'design_request':design_request,
        'from_profile':True,
    }
    return render(request, 'design_requests/design_request_detail.html', context)

@login_required
def design_request_process_request(request, design_request_id):
    """ A view to process the  design requests and redirect to the design request detail """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only site owners can do that.')
        return redirect(reverse('home'))

    design_request = get_object_or_404(DesignRequest, pk=design_request_id)
    order = get_object_or_404(Order, design_request = design_request)

    if request.method == 'POST':
        design_request_form =  OrderFormDesignRequestSuser(request.POST, request.FILES,instance=design_request)

        if design_request_form.is_valid():
            cust_email = order.client.user.email
            design_request = design_request_form.save()
            design_request.save()
            messages.success(request, f'Successfully processed the "{design_request.name}" design request !')
            send_mail (
                'Design request status is now processed',
                f'Your design request:"{design_request.name}" with id : "{design_request.id}" has been sccessfully processed!\
                 Please log into your account to view the processed design request. ',
                settings.DEFAULT_FROM_EMAIL,
                [cust_email]
            )
            return redirect(reverse('design_request_detail', args=[design_request.id]) )
    
        else:
            messages.error(request, 'Failed to process the deisgn request. Please ensure the form is valid.')
    else:
        design_request_form = OrderFormDesignRequestSuser(instance=design_request)
        messages.info(request, f'You are processing design request name :{design_request.name} with Id: {design_request.id}')
    
    context = {
        'design_request_form': design_request_form,
        'design_request':design_request,
    }
    return render(request, 'design_requests/design_request_process_request.html', context)



# Order views 
@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'design_request_session': json.dumps(request.session.get('form_data', {})),
            'save_info': request.POST.get('save_info'),
            'client': request.user,
        })

        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def design_request_checkout(request, design_request_id):
    """ A view for order checkout  """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    
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
                'full_name': request.POST['full_name'],
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
                request.session['form_data']['design_request_id'] =str(f"{design_request.id }")

                # Save the info to the user's profile if all is well
                id_save_info = False if request.POST.get('#id-save-info') == None  else True,
                if id_save_info:
                    request.session['save_info'] = 'save-info' in request.POST

                messages.success(request, f'Order successfully processed! \
                                            Your order number is {order.order_number}. A confirmation \
                                            email will be sent to {order.client.user.email}.\
                                            This is a demonstrative function, your accound will not be charged with any amount')
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
                order_form = OrderFormCheckOut(initial = {
                    'full_name': client.default_full_name,
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

 

    context = {
        
        'stripe_price':stripe_price/100,
        'design_request': design_request,
        'order_form': order_form,
        'stripe_public_key':stripe_public_key,
        'client_secret': intent.client_secret,
        'client_email' : client.user.email
    }

    return render(request, 'design_requests/design_request_checkout.html', context)


def design_request_checkout_success(request, order_number):
    """
    A view that Handles successful checkouts
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
                'default_full_name':order.full_name,
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
