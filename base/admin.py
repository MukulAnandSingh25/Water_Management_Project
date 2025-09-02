from django.contrib import admin
from .models import Restaurant, Bottle, Order, DeliveryPerson, DeliveryAssignment, Notification

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'user')

@admin.register(Bottle)
class BottleAdmin(admin.ModelAdmin):
    list_display = ('id', 'size', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'bottle', 'quantity', 'status', 'order_date')
    list_filter = ('status', 'order_date', 'bottle__size')
    search_fields = ('restaurant__name',)
    actions = ['mark_processing', 'mark_out', 'mark_delivered', 'mark_cancelled']

    def mark_processing(self, request, qs): qs.update(status='PROCESSING')
    mark_processing.short_description = "Mark as Processing"
    def mark_out(self, request, qs): qs.update(status='OUT_FOR_DELIVERY')
    mark_out.short_description = "Mark as Out for Delivery"
    def mark_delivered(self, request, qs): qs.update(status='DELIVERED')
    mark_delivered.short_description = "Mark as Delivered"
    def mark_cancelled(self, request, qs): qs.update(status='CANCELLED')
    mark_cancelled.short_description = "Mark as Cancelled"

admin.site.register(DeliveryPerson)
admin.site.register(DeliveryAssignment)
admin.site.register(Notification)
