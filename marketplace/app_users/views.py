from app_basket.models import Cart, CartItem
from app_merch.models import Offer
from app_settings.models import SiteSettings
from app_users.forms import (ProfileUpdateForm, UserLoginForm,
                             UserPasswordResetForm, UserRegisterForm,
                             UserSetPasswordForm)
from app_users.models import Seller
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from sql_util.utils import SubqueryCount

from .models import Buyer, Profile


class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('pages:index')

    def form_valid(self, form):
        username = form.get_user()
        cart_id = self.request.session.get('cart_id')
        cart_username = Cart.objects.filter(buyer__profile__user__username=username).first()
        if not cart_username:
            Cart.objects.filter(id=int(cart_id)).update(
                buyer=Buyer.objects.create(profile=Profile.objects.get(user__username=username)))
        else:
            cartitems_anonymoususer = CartItem.objects.filter(cart=int(cart_id))
            cartitems_username = CartItem.objects.filter(cart=cart_username.id)
            cartitems_username_offer_ids_list = [cartitem.offer.id for cartitem in cartitems_username]
            for cartitem in cartitems_anonymoususer:
                if cartitem.offer.id not in cartitems_username_offer_ids_list:
                    cartitem.cart = cart_username
                    cartitem.save()

        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('app_users:login')


class CustomPasswordResetView(PasswordResetView):
    form_class = UserPasswordResetForm
    template_name = 'users/password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('app_users:password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = UserSetPasswordForm
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('app_users:password_reset_complete')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomRegisterView(CreateView):
    model = Profile
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('pages:index-page')

    def form_valid(self, form):
        user = form.save()
        Profile.objects.create(user=user,
                               full_name=form.cleaned_data.get('full_name'),
                               phone_number=form.cleaned_data.get('phone_number'),
                               address=form.cleaned_data.get('address'),
                               avatar=form.cleaned_data.get('avatar'))
        return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'users/profile_update.html'
    success_url = '/'


class SellerView(DetailView):
    model = Seller
    template_name = 'seller.html'
    context_object_name = 'seller'

    def get_object(self, queryset=None):
        time_to_cache = SiteSettings.load().time_to_cache
        if not time_to_cache:
            time_to_cache = 1

        return cache.get_or_set(
            f"Seller {self.kwargs.get('pk')}",
            super(SellerView, self).get_object(queryset=None),
            time_to_cache * 60 * 60 * 24
        )

    def get_context_data(self, **kwargs):
        context = super(SellerView, self).get_context_data(**kwargs)
        top_seller_products_cache_time = SiteSettings.load().top_seller_products_cache_time

        if not top_seller_products_cache_time:
            top_seller_products_cache_time = 1

        context['offers'] = cache.get_or_set(
            f"Seller {kwargs.get('pk')} top products",
            Offer.objects.filter(seller=self.get_object()).annotate(
                sales=SubqueryCount('order_items')
            ).order_by('-sales')[:10],
            top_seller_products_cache_time * 60 * 60
        )
        return context
