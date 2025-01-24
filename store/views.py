from django.shortcuts import get_object_or_404, render
from .models import Product, Cart

# Create your views here.

def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products}) #представление главной страницы


# Добавление товаров в корзину
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        # Для неавторизованных пользователей используем сессии
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
    return redirect('home')


 # представление для отображения корзины
def view_cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total = sum(item.total_price() for item in cart_items)
    else:
        cart = request.session.get('cart', {})
        cart_items = []
        total = 0
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': product.price * quantity,
            })
            total += product.price * quantity
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})


# представление для удаления товара из корзины
def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user=request.user, product_id=product_id).first()
        if cart_item:
            cart_item.delete()
    else:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
    return redirect('view_cart')