from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),  # custom logout page

    # Orders
    path('orders/new/', views.place_order_view, name='place_order'),
    path('orders/history/', views.order_history_view, name='order_history'),
    path('invoice/<int:order_id>/', views.order_invoice, name='order_invoice'),
]
