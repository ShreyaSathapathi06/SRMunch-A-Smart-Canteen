from django.db import models

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    category = models.CharField(max_length=50)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)  # NEW

    def __str__(self):
        return self.name



class DailyStock(models.Model):
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    date = models.DateField()
    quantity_available = models.IntegerField()
    quantity_sold = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.food.name} - {self.date}"



# models.py
import random
from django.db import models

def generate_order_id():
    """Generates a unique SRM-XXXXX order ID"""
    from .models import Order  # import here to avoid circular import during migrations
    while True:
        new_id = f"SRM-{random.randint(10000, 99999)}"
        if not Order.objects.filter(order_id=new_id).exists():
            return new_id
        

from django.contrib.auth.models import User

class Order(models.Model):
    order_id = models.CharField(
        max_length=20,
        unique=True,
        default=generate_order_id
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True
    )
    date_time = models.DateTimeField(auto_now_add=True)
    total_amount = models.FloatField()
    payment_method = models.CharField(max_length=20, default="Unknown")

    def __str__(self):
        return f"Order #{self.order_id}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()

    def __str__(self):
        return f"{self.order.order_id} - {self.food.name}"

