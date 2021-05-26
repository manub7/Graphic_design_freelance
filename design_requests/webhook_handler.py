from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from orders.models import Order
from .models import DesignRequest
from .forms import OrderFormCheckOut
from profiles.models import Client

import time
import json


class StripeWH_handler:
    
    """ Handle Stripe webhooks"""
    def __init__(self,request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )        


    def handle_event(self,event):
        """
        Handle a generic/uncknown/unexpected webhook event
        """

        return HttpResponse(
            content = f'Unhandled webhook received: {event["type"]}',
            status = 200
        )

    def handle_payment_intent_succeeded(self,event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        print(pid)
        order = intent.metadata.design_request_session
        #print(json.loads(order).items())
        design_request_id = json.loads(order)['design_request_id']
        design_request = get_object_or_404(DesignRequest, id = design_request_id)    

        save_info = intent.metadata.save_info
    
        client = intent.metadata.client
        client = Client.objects.get(user__username=client)

        shipping_details = intent.shipping
        #Clean data in the billing details

        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        order_exists = False
        attempt= 1
        while attempt <= 5:
            try:
                order = Order.objects.get(

                    full_name__iexact = shipping_details.name,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    design_request = design_request,
                    stripe_pid=pid,

                    )
                order_exists = True
                break
                return HttpResponse(
                    content = f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                    status = 200)

            except Order.DoesNotExist:
                attempt += 1
                time.sleep(0)
            # Create the order 
        if order_exists == True:
            self._send_confirmation_email(order)
            return HttpResponse(
                content = f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status = 200)
        else:
                order = None
                try:
                    order = Order.objects.create(
                        phone_number=shipping_details.phone,
                        country=shipping_details.address.country,
                        postcode=shipping_details.address.postal_code,
                        full_name = shipping_details.name,
                        town_or_city = shipping_details.address.city,
                        street_address1=shipping_details.address.line1,
                        street_address2=shipping_details.address.line2,
                        county = shipping_details.address.state,
                        design_request=design_request,
                        client=client,
                        price = design_request.price,
                        stripe_pid = pid,
                        )

                    # Pass the order number to design request instance 

                except Exception as e :
                    if order:
                        order.delete()
                    return HttpResponse(
                        content = f'Webhook received: {event["type"]} | ERROR: {e}', 
                        status=500)
        return HttpResponse(
                        content = f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook', 
                        status=500) 


    def handle_payment_intent_payment_failed(self,event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """

        return HttpResponse(
            content = f'Webhook received: {event["type"]}',
            status = 200
        )