from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (AllDiscountView, CatalogView, DiscountDetailView,
                    DiscountListView, IndexView, OrderDeliveryView,
                    OrderPaymentView, OrderPurchaseView, OrderUserDataView,
                    ProductDetailView, ProductPurchaseView, PaymentView, ComparisonView)

app_name = "pages"

urlpatterns = [
    path('', IndexView.as_view(), name='index-page'),
    path('products/', CatalogView.as_view(), name='catalog-view'),
    path('products/all_product_discounts/', AllDiscountView.as_view(), name='all-discounts'),
    path('product_detail/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('product_detail/<int:pk>/purchase/', ProductPurchaseView.as_view(), name='offer-purchase'),
    path('order/userdata/', OrderUserDataView.as_view(), name='order-step-1'),
    path('order/delivery/', OrderDeliveryView.as_view(), name='order-step-2'),
    path('order/payment/', OrderPaymentView.as_view(), name='order-step-3'),
    path('order/purchase/', OrderPurchaseView.as_view(), name='order-step-4'),
    path('order/send-payment/', PaymentView.as_view(), name='payment-view'),
    path("discounts/", DiscountListView.as_view(), name="discount_list"),
    path("discounts/<int:pk>/", DiscountDetailView.as_view(), name="discount_detail"),
    path("comparison/", ComparisonView.as_view(), name="comparison"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
