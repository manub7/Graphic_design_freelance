from django.urls import path 
from . import views

urlpatterns = [
    path('', views.all_orders, name ="orders"),
    path('<int:product_id>', views.order_detail, name ="order_detail"),
]