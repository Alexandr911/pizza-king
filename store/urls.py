from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'), #Home
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'), #товар в корзинy
    path('cart/', views.view_cart, name='view_cart'), #URL для отображения корзины
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'), # URL для удаления товара из корзины
    path('create_order/', views.create_order, name='create_order'), # URL для оформления заказа
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'), # URL для личного кабинета
    path('order/<int:order_id>/', views.order_detail, name='order_detail'), # URL для просмотра деталей заказа
    path('accounts/login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('payment/process/', views.payment_process, name='payment_process'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'), #Обработка платижей
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('coupon/apply/', views.coupon_apply, name='coupon_apply'),#URL для применения купона
    path('product/<int:product_id>/add_review/', views.add_review, name='add_review'),# URL для добавления отзыва
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),#для add товара из избранного
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'), #для удаления товара из избранного


]