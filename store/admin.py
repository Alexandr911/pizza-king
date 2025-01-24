from django.contrib import admin
from .models import Product, Cart, Order, OrderItem
from .models import Profile, Promotion

# модели для администрирования
# класс OrderItemInline для отображения товаров заказа
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


# Настройки для отображения модели Order в админке
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'address', 'phone', 'paid', 'created_at', 'updated_at']
    list_filter = ['paid', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

# Настройки для отображения модели Product в админке.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']
    list_filter = ['category']
    search_fields = ['name', 'description']

# Настройки для отображения модели Cart в админке.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity']
    list_filter = ['user']

# Настройки для отображения модели Profile в админке.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'address']
    search_fields = ['user__username', 'phone', 'address']

# Models акций
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'active']
    list_filter = ['active']
    search_fields = ['title', 'description']