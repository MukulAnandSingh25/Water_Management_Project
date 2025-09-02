from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime

from .models import Restaurant, Bottle, Order, Notification
from .forms import (
    RestaurantRegisterForm, PlaceOrderForm,
    OrderFilterForm, RestaurantProfileForm
)

def home_view(request):
    return render(request, 'home.html')

# --- Auth / Register ---
def register_view(request):
    if request.method == 'POST':
        form = RestaurantRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            Restaurant.objects.create(
                user=user,
                name=form.cleaned_data['restaurant_name'],
                address=form.cleaned_data.get('address', ''),
                phone=form.cleaned_data.get('phone', '')
            )
            return redirect('login')
    else:
        form = RestaurantRegisterForm()
    return render(request, 'register.html', {'form': form})

# --- Dashboard ---
@login_required
def dashboard_view(request):
    restaurant = request.user.restaurant
    orders = restaurant.orders.select_related('bottle').order_by('-order_date')[:5]

    total_orders = restaurant.orders.count()
    delivered = restaurant.orders.filter(status='DELIVERED').count()
    pending = restaurant.orders.exclude(status='DELIVERED').count()
    total_spent = restaurant.orders.aggregate(total=Sum('bottle__price'))['total']  # quick indicator

    notifications = restaurant.notifications.all()[:5]
    return render(request, 'dashboard.html', {
        'orders': orders,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending,
        'notifications': notifications,
        'total_spent': total_spent or 0
    })

# --- Place Order (user cannot set status) ---
@login_required
def place_order_view(request):
    restaurant = request.user.restaurant
    if request.method == 'POST':
        form = PlaceOrderForm(request.POST, restaurant=restaurant)
        if form.is_valid():
            order = form.save(commit=False)
            order.restaurant = restaurant
            order.status = 'PENDING'
            order.save()
            Notification.objects.create(
                restaurant=restaurant,
                message=f"Order #{order.pk} placed successfully."
            )
            return redirect('order_history')
    else:
        form = PlaceOrderForm(restaurant=restaurant)
    return render(request, 'place_order.html', {'form': form})

# --- Order history with filters ---
@login_required
def order_history_view(request):
    restaurant = request.user.restaurant
    qs = restaurant.orders.select_related('bottle').order_by('-order_date')

    form = OrderFilterForm(request.GET or None)
    if form.is_valid():
        status = form.cleaned_data.get('status')
        size = form.cleaned_data.get('size')
        df = form.cleaned_data.get('date_from')
        dt = form.cleaned_data.get('date_to')
        if status:
            qs = qs.filter(status=status)
        if size:
            qs = qs.filter(bottle__size=size)
        if df:
            qs = qs.filter(order_date__date__gte=df)
        if dt:
            qs = qs.filter(order_date__date__lte=dt)

    return render(request, 'order_history.html', {'orders': qs, 'filter_form': form})

# --- Invoice (PDF) ---
@login_required
def order_invoice_pdf(request, order_id):
    order = get_object_or_404(Order, pk=order_id, restaurant=request.user.restaurant)
    # Simple HTML to PDF using xhtml2pdf
    html = render(request, 'invoice.html', {'order': order}).content.decode('utf-8')
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('utf-8')), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse("Error generating PDF", status=500)

# --- Profile ---
@login_required
def profile_view(request):
    restaurant = request.user.restaurant
    if request.method == 'POST':
        form = RestaurantProfileForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            Notification.objects.create(restaurant=restaurant, message="Profile updated.")
            return redirect('profile')
    else:
        form = RestaurantProfileForm(instance=restaurant)
    return render(request, 'profile.html', {'form': form})


def order_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "invoice.html", {"order": order})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")   # redirect to login page after logout
    return render(request, "logout.html")