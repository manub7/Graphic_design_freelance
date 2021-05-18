
from django.contrib import admin
from django.urls import path 
from . import views

urlpatterns = [
    path('', views.add_design_requests, name ="add_design_requests"),
    path('<int:order_id>/', views.design_request_detail, name ="design_request_detail"),
    #path('checkout/', views.checkout, name="checkout"),
]