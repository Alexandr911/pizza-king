from django import forms
from .models import Order, Profile

# форма для оформления заказа
class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'phone']



# формa для редактирования профиля
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address']

# форма для применения купона
class CouponApplyForm(forms.Form):
    code = forms.CharField(label='Gutscheincode')
