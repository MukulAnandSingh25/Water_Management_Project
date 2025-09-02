from django.db import models
from django.contrib.auth.models import User

# --- Restaurant profile tied to a user ---
class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant')
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

# --- Bottles & pricing (admin can update) ---
class Bottle(models.Model):
    SIZE_CHOICES = [
        ('500ML', '500ml'),
        ('1L', '1L'),
        ('2L', '2L'),
    ]
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price per bottle

    def __str__(self):
        return dict(self.SIZE_CHOICES).get(self.size, self.size)

# --- Orders with rich statuses ---
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    bottle = models.ForeignKey(Bottle, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)

    @property
    def subtotal(self):
        return self.quantity * self.bottle.price

    def __str__(self):
        return f"Order #{self.pk} | {self.restaurant.name} | {self.get_status_display()}"

# --- Optional: assign a delivery person (admin only) ---
class DeliveryPerson(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class DeliveryAssignment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    person = models.ForeignKey(DeliveryPerson, on_delete=models.PROTECT)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order} → {self.person}"

# --- Simple in-app notifications (when status changes) ---
class Notification(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notify({self.restaurant.name}): {self.message[:30]}..."
