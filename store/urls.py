from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), #Home
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'), #товар в корзинy
    path('cart/', views.view_cart, name='view_cart'), #URL для отображения корзины
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'), # URL для удаления товара из корзины

]