from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Restaurant, Order, Bottle

# Register: user + restaurant info
class RestaurantRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    restaurant_name = forms.CharField(label='Restaurant Name', max_length=150)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                  'restaurant_name', 'address', 'phone']

# Place order with dynamic min qty
class PlaceOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['bottle', 'quantity', 'notes']

    def __init__(self, *args, **kwargs):
        self.restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        self.fields['bottle'].queryset = Bottle.objects.all()
        self.fields['quantity'].widget.attrs.update({'placeholder': 'Minimum depends on bottle size'})

    def clean_quantity(self):
        qty = self.cleaned_data['quantity']
        bottle = self.cleaned_data.get('bottle')

        # Dynamic minimums (adjust if you want)
        min_map = {'500ML': 50, '1L': 50, '2L': 50}
        if bottle:
            min_required = min_map.get(bottle.size, 50)
        else:
            min_required = 50

        if qty < min_required:
            raise forms.ValidationError(f"Minimum for {bottle} is {min_required} bottles.")
        return qty

# Filtering the history
class OrderFilterForm(forms.Form):
    status = forms.ChoiceField(choices=[('', 'All')] + list(Order.STATUS_CHOICES), required=False)
    size = forms.ChoiceField(choices=[('', 'All')] + list(Bottle.SIZE_CHOICES), required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type':'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type':'date'}))

# Profile edit
class RestaurantProfileForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'phone']
