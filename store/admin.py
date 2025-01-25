from django.contrib import admin
from .models import Product, Cart, Order, OrderItem
from .models import Profile, Promotion, Ingredient
from .models import Slide, Category
from django.utils.html import format_html

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


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']

# Настройки для отображения модели Product в админке
# изображений через административную панель
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'category', 'display_image']
    list_filter = ['category']
    search_fields = ['name', 'description']
    filter_horizontal = ['ingredients']  # Удобный выбор ингредиентов
    fieldsets = [
        (None, {'fields': ['name', 'description', 'price', 'category']}),
        ('Details', {'fields': ['image', 'composition', 'weight', 'size']}),
    ]

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Image'

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


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')

