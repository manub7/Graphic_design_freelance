
from django.contrib import admin
from django.urls import path 
from . import views

urlpatterns = [
    path('', views.design_request_list, name ="design_request_list"),
    path('add_design_requests/', views.add_design_requests, name ="add_design_requests"),
    path('design_request_detail/<int:design_request_id>/', views.design_request_detail, name ="design_request_detail"),
    path('design_request_checkout/<int:design_request_id>/', views.design_request_checkout, name="design_request_checkout"),
    path('design_request_process_request/<int:design_request_id>/', views.design_request_process_request, name="design_request_process_request"),
    path('design_request_testimonial/<int:design_request_id>/', views.design_request_testimonial, name="design_request_testimonial"),
    path('design_request_checkout_success/<order_number>/', views.design_request_checkout_success, name="design_request_checkout_success"),
]