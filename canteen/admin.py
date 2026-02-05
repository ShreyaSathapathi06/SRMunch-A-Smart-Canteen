from django.contrib import admin
from .models import FoodItem, DailyStock, Order, OrderItem

admin.site.register(FoodItem)
admin.site.register(DailyStock)
admin.site.register(Order)
admin.site.register(OrderItem)


# Register your models here.
