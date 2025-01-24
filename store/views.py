from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import OrderCreateForm, ProfileForm
from .models import Cart, OrderItem, Order
from .models import Product, Promotion, Profile


# Create your views here.

def home(request):
    products = Product.objects.all()
    promotions = Promotion.objects.filter(active=True)
    return render(request, 'store/home.html', {'products': products, 'promotions': promotions}) #представление главной страницы


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


# представление для оформления заказа
def create_order(request):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            if request.user.is_authenticated:
                cart_items = Cart.objects.filter(user=request.user)
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        price=item.product.price,
                        quantity=item.quantity,
                    )
                cart_items.delete()
            else:
                cart = request.session.get('cart', {})
                for product_id, quantity in cart.items():
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=product.price,
                        quantity=quantity,
                    )
                del request.session['cart']

            return render(request, 'store/order_created.html', {'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'store/create_order.html', {'form': form})



# представления для отображения и редактирования профиля
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/profile.html', {'profile': profile, 'orders': orders})

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'store/edit_profile.html', {'form': form})


# представление для просмотра деталей заказа
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})