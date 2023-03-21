from django.urls import path
from . import views


urlpatterns = [
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('products', views.all_products, name='products'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart', views.get_cart, name='cart'),
    path('create_order', views.create_order, name='create_order'),
    path('orders', views.get_orders, name='orders'),
    path('product/create', views.create_product, name='create_product'),
    path('product/<int:product_id>/edit', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/delete', views.delete_product, name='delete_product'),
]
