
from django.contrib import admin
from django.urls import path 
from . import views

urlpatterns = [
    path('', views.add_design_requests, name ="add_design_requests"),
    path('design_request_detail/<int:design_request_id>/', views.design_request_detail, name ="design_request_detail"),
    path('design_request_checkout/<int:design_request_id>/', views.design_request_checkout, name="design_request_checkout"),
]