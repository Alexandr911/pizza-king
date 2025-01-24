from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import OrderCreateForm, ProfileForm, CouponApplyForm, ReviewForm
from .models import Cart, OrderItem, Order, Coupon,Recommendation
from .models import Product, Promotion, Profile
from .models import Review, Wishlist, ProductView
import stripe
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.db.models import Count, Avg
from django.core.cache import cache
import logging






#представление главной страницы
def home(request):
    products = cache.get('products')
    if not products:
        products = Product.objects.all()
        cache.set('products', products, 60 * 15)  # Кэшируем на 15 минут

    promotions = Promotion.objects.filter(active=True)

    recommendations = []
    if request.user.is_authenticated:
        recommendations = Recommendation.objects.filter(user=request.user).order_by('-score')[:5]
        logger.info(f"Recommendations for {request.user.username}: {list(recommendations)}")  # Логирование

    return render(request, 'store/home.html', {
        'products': products,
        'promotions': promotions,
        'recommendations': recommendations,
    })

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


 # представление для отображения корзины +  учета скидок
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

    coupon_id = request.session.get('coupon_id')
    coupon = None
    if coupon_id:
        coupon = Coupon.objects.get(id=coupon_id)
        discount = (coupon.discount / 100) * total
        total -= discount

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'coupon': coupon,
    })


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


# представление для оформления заказа + оплата + отправка маил
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

            request.session['order_id'] = order.id
            send_order_email(order, 'emails/order_created.html', 'Bestellbestätigung')
            return redirect('payment_process')
    else:
        form = OrderCreateForm()
    return render(request, 'store/create_order.html', {'form': form})



# представления для отображения и редактирования профиля + отображения избраного+ истории просмотров
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user)
    wishlist = Wishlist.objects.filter(user=request.user)
    viewed_products = ProductView.objects.filter(user=request.user).order_by('-viewed_at')[:10]  # Последние 10 просмотров
    return render(request, 'store/profile.html', {
        'profile': profile,
        'orders': orders,
        'wishlist': wishlist,
        'viewed_products': viewed_products,
    })

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


# представление для обработки платежей
stripe.api_key = settings.STRIPE_SECRET_KEY
def payment_process(request):
    order_id = request.session.get('order_id')
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment_success'))
        cancel_url = request.build_absolute_uri(reverse('payment_cancel'))
        session_data = {
            'payment_method_types': ['card'],
            'line_items': [{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'Order #{order.id}',
                    },
                    'unit_amount': int(order.get_total_cost() * 100),
                },
                'quantity': 1,
            }],
            'mode': 'payment',
            'success_url': success_url,
            'cancel_url': cancel_url,
        }
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)
    else:
        return render(request, 'store/payment_process.html', {'order': order, 'stripe_public_key': settings.STRIPE_PUBLIC_KEY})


# представления для успешного и отмененного платежа
def payment_success(request):
    order_id = request.session.get('order_id')
    order = Order.objects.get(id=order_id)
    order.paid = True
    order.save()

    if order.user:
        generate_recommendations(order.user)  # Проверьте, что эта строка есть

    send_order_email(order, 'emails/order_paid.html', 'Zahlungsbestätigung')
    return render(request, 'store/payment_success.html', {'order': order})


def payment_cancel(request):
    return render(request, 'store/payment_cancel.html')


# функция для отправки email
def send_order_email(order, template, subject):
    html_message = render_to_string(template, {'order': order})
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        'noreply@pizza-king.com',  # Отправитель (можно указать любой email)
        [order.email],             # Получатель (email заказчика)
        html_message=html_message,
    )


# представление для применения купона
def coupon_apply(request):
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(
                code__iexact=code,
                valid_from__lte=now,
                valid_to__gte=now,
                active=True
            )
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    return redirect('view_cart')


# представление для добавления отзыва
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()
    return render(request, 'store/add_review.html', {'form': form, 'product': product})


# Отображение отзывов на странице товара
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    return render(request, 'store/product_detail.html', {'product': product, 'reviews': reviews})


# Генерация рекомендаций
logger = logging.getLogger(__name__)

def generate_recommendations(user):
    # Получаем товары, которые пользователь уже покупал
    purchased_products = OrderItem.objects.filter(order__user=user).values_list('product', flat=True)
    logger.info(f"Purchased products: {list(purchased_products)}")

    # Получаем товары с высоким рейтингом, которые пользователь еще не покупал
    recommended_products = Product.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).exclude(id__in=purchased_products).order_by('-avg_rating', '-review_count')[:5]
    logger.info(f"Recommended products: {list(recommended_products)}")

    # Сохраняем рекомендации
    for product in recommended_products:
        Recommendation.objects.create(user=user, product=product, score=product.avg_rating)


# представление для добавления товара в избранное
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('product_detail', product_id=product.id)

# Удаление товаров из избранного
@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect('profile')


# Добавление товаров в историю просмотров
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()

    # Сохраняем просмотр товара
    if request.user.is_authenticated:
        ProductView.objects.create(user=request.user, product=product)
    else:
        ProductView.objects.create(product=product)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
    })
