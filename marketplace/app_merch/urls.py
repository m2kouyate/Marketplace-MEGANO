from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import CategoryView, IndexView

app_name = 'pages'

urlpatterns = [
    path('', IndexView.as_view(), name='index-page'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
