from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (CustomLoginView, CustomLogoutView,
                    CustomPasswordResetConfirmView,
                    CustomPasswordResetDoneView, CustomPasswordResetView,
                    CustomRegisterView, SellerView, AccountView, ProfileEditView, OrdersHistoryView, ViewsHistoryView)

app_name = 'app_users'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('seller/<int:pk>/', SellerView.as_view(), name='seller_detail'),
    path('profile/<slug:username>/', AccountView.as_view(), name='account'),
    path('profile/<slug:username>/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('my/orders/', OrdersHistoryView.as_view(), name='orders_history'),
    path('profile/<slug:username>/views/', ViewsHistoryView.as_view(), name='views_history'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
