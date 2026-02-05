from django.shortcuts import render, redirect
from .models import DailyStock, Order, OrderItem
from datetime import date
from django.http import JsonResponse

# -------------------------
# MENU PAGE
# -------------------------
# -------------------------
# MENU PAGE
# -------------------------
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localdate

@login_required(login_url='student_login')
def menu(request):
    today = localdate()

    stocks = DailyStock.objects.filter(
        date=today,
        quantity_available__gt=0
    ).select_related('food')

    categories = {}
    for stock in stocks:
        cat = stock.food.category
        categories.setdefault(cat, []).append(stock)

    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())
    cart_total = 0
    cart_items = []

    for stock_id, qty in cart.items():
        try:
            stock = DailyStock.objects.get(id=int(stock_id))
            total = stock.food.price * qty
            cart_total += total
            cart_items.append({
                'id': stock.id,
                'name': stock.food.name,
                'price': stock.food.price,
                'qty': qty,
                'total': total,
                'stock_quantity': stock.quantity_available
            })
        except DailyStock.DoesNotExist:
            pass

    response = render(request, 'canteen/menu.html', {
        'categories': categories,
        'cart_count': cart_count,
        'cart_total': cart_total,
        'cart_items': cart_items,
    })

    response['Cache-Control'] = 'no-store'
    return response

# -------------------------
# ADD TO CART (FORM SUBMIT)
# -------------------------
def add_to_cart(request, stock_id):
    cart = request.session.get('cart', {})
    stock = DailyStock.objects.get(id=stock_id)

    stock_id = str(stock_id)
    current_qty = cart.get(stock_id, 0)

    if current_qty < stock.quantity_available:
        cart[stock_id] = current_qty + 1
    else:
        from django.contrib import messages
        messages.error(request, "Not enough stock available")

    request.session['cart'] = cart
    request.session.modified = True


    # 🔥 GO BACK TO SAME PLACE
    return redirect(request.META.get('HTTP_REFERER', 'menu'))

    

# -------------------------
# CART PAGE
# -------------------------
# -------------------------
# VIEW CART PAGE
# -------------------------
from django.contrib.auth.decorators import login_required

@login_required(login_url='student_login')
def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for stock_id, qty in cart.items():
        try:
            stock = DailyStock.objects.get(id=int(stock_id))
            item_total = stock.food.price * qty
            total += item_total

            items.append({
                'id': stock.id,
                'name': stock.food.name,
                'price': stock.food.price,
                'quantity': qty,
                'total': item_total,
                'stock_quantity': stock.quantity_available
            })
        except DailyStock.DoesNotExist:
            pass

    response = render(request, 'canteen/cart.html', {
        'items': items,
        'total': total
    })

    response['Cache-Control'] = 'no-store'
    return response



# -------------------------
# REMOVE ITEM
# -------------------------
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})

    if str(item_id) in cart:
        del cart[str(item_id)]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('view_cart')


# -------------------------
# PLACE ORDER
# -------------------------
import random


def generate_unique_order_id():
    from .models import Order
    while True:
        new_id = f"SRM-{random.randint(10000, 99999)}"
        if not Order.objects.filter(order_id=new_id).exists():
            return new_id

from .models import DailyStock, Order, OrderItem
from django.shortcuts import render
from django.utils import timezone
@login_required(login_url='student_login')
def payment_success(request):
    cart = request.session.get('cart', {})
    if not cart:
        return render(request, 'canteen/order_success.html', {'items': [], 'total': 0, 'order': None, 'payment_method': 'Unknown'})

    items = []
    total = 0
    payment_method = request.GET.get('method', 'Unknown')

    # 1️⃣ Create the Order object first
    order = Order.objects.create(
        user=request.user,        # ✅ FIX
        total_amount=0,
        payment_method=payment_method
    )

    # 2️⃣ Loop through cart to create OrderItems
    for stock_id, qty in cart.items():
        stock = DailyStock.objects.get(id=int(stock_id))
        subtotal = stock.food.price * qty
        total += subtotal

        OrderItem.objects.create(
            order=order,
            food=stock.food,
            quantity=qty,
            price=stock.food.price
        )

        # reduce stock
        stock.quantity_available -= qty
        stock.save()

        items.append({
            'name': stock.food.name,
            'price': stock.food.price,
            'qty': qty,
            'subtotal': subtotal
        })

    # 3️⃣ Update total_amount in the order now that we know it
    order.total_amount = total
    order.save()

    # 4️⃣ Clear cart
    request.session['cart'] = {}

    # 5️⃣ Render template with order object
    return render(request, 'canteen/order_success.html', {
        'items': items,
        'total': total,
        'order': order,
        'payment_method': payment_method
    })
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from xhtml2pdf import pisa
from .models import Order, OrderItem
import os

def download_receipt(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return HttpResponse("Order not found.", status=404)

    items = OrderItem.objects.filter(order=order)

    # Absolute path to logo
    logo_path = os.path.join(settings.BASE_DIR, "canteen", "static", "canteen", "logo.png")

    html = render_to_string('canteen/order_receipt.html', {
        'order': order,
        'items': items,
        'logo_path': logo_path,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Order_{order.order_id}.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response



# AJAX INCREASE / DECREASE
# -------------------------
def ajax_increase_cart(request, stock_id):
    cart = request.session.get('cart', {})
    stock = DailyStock.objects.get(id=stock_id)

    stock_id_str = str(stock_id)
    current_qty = cart.get(stock_id_str, 0)

    # HARD STOCK CHECK
    if current_qty >= stock.quantity_available:
        return JsonResponse({
            'error': 'Not enough stock available!',
            'item_qty': current_qty
        })

    # Increase
    cart[stock_id_str] = current_qty + 1
    request.session['cart'] = cart

    # Calculate totals
    total_amount = sum(
        DailyStock.objects.get(id=int(s_id)).food.price * qty
        for s_id, qty in cart.items()
    )

    return JsonResponse({
        'cart_count': sum(cart.values()),
        'cart_total': total_amount,
        'item_qty': cart[stock_id_str],
        'item_name': stock.food.name,        # ✅ Add name
        'item_price': stock.food.price,      # ✅ Add price
        'item_total': stock.food.price * cart[stock_id_str]  # ✅ total for this item
    })



def ajax_decrease_cart(request, stock_id):
    cart = request.session.get('cart', {})
    stock_id_str = str(stock_id)

    if stock_id_str in cart:
        if cart[stock_id_str] > 1:
            cart[stock_id_str] -= 1
        else:
            del cart[stock_id_str]

    request.session['cart'] = cart
    request.session.modified = True


    # Calculate totals
    total_qty = sum(cart.values())
    total_amount = 0
    for s_id, qty in cart.items():
        s = DailyStock.objects.get(id=int(s_id))
        total_amount += s.food.price * qty

    return JsonResponse({
        'cart_count': total_qty,
        'cart_total': total_amount,
        'item_qty': cart.get(stock_id_str, 0)
    })
def clear_cart(request):
    request.session['cart'] = {}
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # If AJAX request, return JSON
        return JsonResponse({'cart_total': 0, 'cart_count': 0})
    return redirect('view_cart')

@login_required(login_url='student_login')
def payment_page(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('menu')

    # calculate total
    total = 0
    for stock_id, qty in cart.items():
        stock = DailyStock.objects.get(id=int(stock_id))
        total += stock.food.price * qty

    return render(request, 'canteen/payment.html', {'total': total})
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, DailyStock

@login_required(login_url='student_login')
def place_order(request):
    if request.method != "POST":
        return redirect('menu')

    payment_method = request.POST.get('payment_method', 'Unknown')

    cart = request.session.get('cart', {})
    if not cart:
        return redirect('menu')

    items = []
    total = 0

    # 1️⃣ Create Order object (LINK USER HERE)
    order = Order.objects.create(
        user=request.user,              # ✅ THIS WAS MISSING
        total_amount=0,                 # temp
        payment_method=payment_method
        # ❌ DO NOT pass order_id (model handles it)
    )

    # 2️⃣ Create OrderItems & reduce stock
    for stock_id, qty in cart.items():
        stock = DailyStock.objects.get(id=int(stock_id))
        subtotal = stock.food.price * qty
        total += subtotal

        OrderItem.objects.create(
            order=order,
            food=stock.food,
            quantity=qty,
            price=stock.food.price
        )

        stock.quantity_available -= qty
        stock.quantity_sold += qty
        stock.save()

        items.append({
            'name': stock.food.name,
            'price': stock.food.price,
            'qty': qty,
            'subtotal': subtotal
        })

    # 3️⃣ Update total
    order.total_amount = total
    order.save()

    # 4️⃣ Clear cart
    request.session['cart'] = {}

    # 5️⃣ Success page
    return render(request, 'canteen/order_success.html', {
        'items': items,
        'total': total,
        'order': order,
        'payment_method': payment_method
    })
from django.contrib.auth.decorators import login_required
from .models import Order

from django.contrib.auth.decorators import login_required
from canteen.models import Order

@login_required
def student_profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-date_time')

    return render(request, 'canteen/student_profile.html', {
        'orders': orders,
        'student_profile': request.user.studentprofile
    })

from django.contrib.auth.decorators import login_required

@login_required(login_url='student_login')
def edit_profile(request):
    profile = request.user.studentprofile

    if request.method == "POST":
        profile.full_name = request.POST.get("full_name", "")

        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES["profile_pic"]

        profile.save()
        return redirect('student_profile')

    return render(request, 'canteen/edit_profile.html', {
        'profile': profile
    })
from django.contrib.auth.decorators import login_required