from django import forms
from django.core import validators
from .models import Offer, Review


class ReviewForm(forms.ModelForm):
    # seller = forms.ModelChoiceField(queryset=Seller.objects.all(), label='Продавец')

    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'rating', 'min': 1, 'max': 5}),
            'text': forms.Textarea(attrs={'rows': 5})
        }


class PurchaseForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)

    def __init__(self, *args, **kwargs):
        offer = kwargs.pop('offer')
        super().__init__(*args, **kwargs)
        self.offer = offer
        self.fields['quantity'].max_value = offer.quantity

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity > self.offer.quantity:
            raise forms.ValidationError("Недостаточно товара для заказа.")
        return quantity


class OrderUserDataForm(forms.Form):
    """ Форма для первого шага оформления заказа. """

    name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-input'}),
        label='ФИО',
    )
    phone = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-input'}),
        label='Телефон',
        error_messages={'invalid': 'Введите корректный Телефон'}
    )
    mail = forms.EmailField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-input'}),
        label='E-mail',
        error_messages={'invalid': 'Введите корректный E-mail'}
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if not self.request:
            return

        self.user_data = self.request.session.get('user_data')
        if self.request.user.is_authenticated:
            name = self.user_data.get('name')[0] if self.user_data else self.request.user.profile.full_name
            phone = self.user_data.get('phone')[0] if self.user_data else self.request.user.profile.phone_number
            mail = self.user_data.get('mail')[0] if self.user_data else self.request.user.email

            self.fields['name'].initial = name
            self.fields['phone'].initial = phone
            self.fields['mail'].initial = mail


class OrderDeliveryDataForm(forms.Form):
    """ Форма для второго шага оформления заказа. """

    city = forms.CharField(max_length=100, required=True, widget=forms.TextInput(
        attrs={'class': 'form-input', 'data-validate': 'require'}),
        label='Город',
        error_messages={'required': 'Поле "Город" обязательно для заполнения'}
    )
    address = forms.CharField(max_length=500, required=True, widget=forms.Textarea(
        attrs={'class': 'form-textarea', 'data-validate': 'require'}),
        label='Адрес',
        error_messages={'required': 'Поле "Адрес" обязательно для заполнения'}
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if not self.request:
            return

        self.delivery_data = self.request.session.get('user_data')
        if self.delivery_data:
            self.delivery_data = self.delivery_data.get('delivery_data')

        if self.delivery_data:
            city = self.delivery_data.get('city')[0] if self.delivery_data else ''
            address = self.delivery_data.get('address')[0] if self.delivery_data else ''

            self.fields['city'].initial = city
            self.fields['address'].initial = address
