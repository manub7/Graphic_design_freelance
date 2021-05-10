
from django.contrib import admin
from django.urls import path 
from . import views

urlpatterns = [
    path('', views.design_requests, name ="design_requests")
]