from django.contrib import admin

from .models import Buyer, Profile, Seller


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', ]
    search_fields = ['full_name', ]


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', ]
    search_fields = ['title', ]


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ['profile']
    search_fields = ['profile']
