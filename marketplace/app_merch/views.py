from copy import copy

from django.db.models import QuerySet, Min, Max, Count
from django.views.generic import ListView
from mptt.querysets import TreeQuerySet

from . import review_service
from .models import (
    Category,
    Product,
    Banner,
    Discount,
    Offer,
    Review,
    Tag
)
from app_settings.models import SiteSettings
from app_users.models import Profile, Seller
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from . import review_service
from .forms import ReviewForm


class IndexView(ListView):
    """ Вью класс для главной страницы MEGANO. """
    template_name = 'index.html'
    context_object_name = 'products'
    model = Product

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        banners_cache_time = SiteSettings.load().banners_cache_time

        if not banners_cache_time:
            banners_cache_time = 10

        context['banners'] = cache.get_or_set(
            'Banners',
            Banner.objects.filter(is_active=True).order_by('?')[:3],
            banners_cache_time * 60
        )

        return context


class CategoryView(ListView):
    """ Вью класс получения активных категорий товаров. """
    template_name = 'base.html'
    context_object_name = 'categories'

    def get_queryset(self):
        """ Получаем доступные категории и кешируем их на 1 день. """
        time_to_cache = SiteSettings.load().time_to_cache
        if not time_to_cache:
            time_to_cache = 1

        return cache.get_or_set(
            f"Categories",
            Category.objects.filter(is_active=True),
            time_to_cache * 60 * 60 * 24
        )


class AllDiscountView(ListView):
    """ View для получения всех активных скидок. """
    template_name = 'base.html'
    context_object_name = 'all_discounts'

    def get_queryset(self):
        """ Получаем все доступные скидки и кешируем их на 1 день. """
        time_to_cache = SiteSettings.load().time_to_cache
        if not time_to_cache:
            time_to_cache = 1

        return cache.get_or_set(
            f"Discounts",
            Discount.objects.filter(is_active=True),
            time_to_cache * 60 * 60 * 24
        )


class PriorityDiscountView(ListView):
    """ View для получения приоритетных скидок. """
    template_name = 'base.html'
    context_object_name = 'priority_discounts'

    def get_queryset(self):
        """ Получаем приоритетные скидки и кешируем их на 1 день. """
        time_to_cache = SiteSettings.load().time_to_cache
        if not time_to_cache:
            time_to_cache = 1

        return cache.get_or_set(
            f"Priority_discounts",
            Discount.objects.filter(is_priority=True),
            time_to_cache * 60 * 60 * 24
        )


class CatalogView(ListView):
    """ Вью класс для получения списка товаров и отображения их в каталоге. """
    template_name = 'catalog.html'
    context_object_name = 'offers'
    paginate_by = 8

    def get_queryset(self):
        """
        Получение списка товаров по фильтру и сортировке.
        Список кешируется на 1 день.
        """
        queryset: QuerySet = Offer.objects.filter(is_active=True)

        time_to_cache: int = SiteSettings.load().time_to_cache
        if not time_to_cache:
            time_to_cache = 1

        price_range: str = self.request.GET.get('price')
        title: str = self.request.GET.get('title')
        in_stock: str = self.request.GET.get('in_stock')
        delivery_free: str = self.request.GET.get('delivery_free')
        slug: str = self.request.GET.get('cat')
        tag = self.request.GET.get('tag')

        price_sort: str = self.request.GET.get('price_sort')
        created_at_sort: str = self.request.GET.get('created_at_sort')
        reviews_sort: str = self.request.GET.get('reviews_sort')
        purchase_sort: str = self.request.GET.get('purchase_sort')

        if slug and slug != 'all':
            category: Category = Category.objects.get(slug=slug)
            sub_categories: TreeQuerySet = category.get_descendants(include_self=True)

            queryset: QuerySet = Offer.objects.select_related('product__category').filter(
                product__category__in=sub_categories).filter(is_active=True)
        if price_range:
            min_price, max_price = price_range.split(';')[0], price_range.split(';')[1]
            queryset: QuerySet = queryset.filter(price__range=(min_price, max_price))
        if title:
            queryset: QuerySet = queryset.filter(product__title__icontains=title)
        if in_stock:
            queryset: QuerySet = queryset.filter(quantity__gt=0)
        if delivery_free:
            queryset: QuerySet = queryset.filter(is_delivery_free=True)
        if tag:
            queryset: QuerySet = queryset.filter(product__tags__pk=tag)

        if price_sort in ('-price', 'price'):
            queryset: QuerySet = queryset.order_by(price_sort)
        if created_at_sort in ('-created_at', 'created_at'):
            queryset: QuerySet = queryset.order_by(created_at_sort)
        if reviews_sort in ('desc', 'asc'):
            queryset: QuerySet = queryset.annotate(review_amount=Count('reviews'))
            if reviews_sort == 'desc':
                queryset: QuerySet = queryset.order_by('-review_amount')
            else:
                queryset: QuerySet = queryset.order_by('review_amount')
        if purchase_sort in ('desc', 'asc'):
            queryset: QuerySet = queryset.annotate(purchases=Count('orders'))
            if purchase_sort == 'desc':
                queryset: QuerySet = queryset.order_by('-purchases')
            else:
                queryset: QuerySet = queryset.order_by('purchases')

        return cache.get_or_set(
            f"Catalog_{slug}_{price_range}_"
            f"{title}_{in_stock}_"
            f"{delivery_free}_{tag}_"
            f"{price_sort}_{created_at_sort}_"
            f"{reviews_sort}_{purchase_sort}",
            queryset,
            time_to_cache * 60 * 60 * 24
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Получение контекста для корректного вывода отфильтрованных товаров.
        Контекст наполняется информацией касательно: тегов, макс. и мин. цены,
        категории, наименовании товара, нахождении товара в наличии, различной сортировки.
        Данные о минимальной и максимальной цене добавляются в сессию для
        последующего получения значения из неё.
        """
        context = super().get_context_data(**kwargs)

        context['tags'] = Tag.objects.all()[:5]

        price_range: str = self.request.GET.get('price')
        category: str = self.request.GET.get('cat')
        title: str = self.request.GET.get('title')
        in_stock: str = self.request.GET.get('in_stock')
        delivery_free: str = self.request.GET.get('delivery_free')

        price_sort: str = self.request.GET.get('price_sort')
        created_at_sort: str = self.request.GET.get('created_at_sort')
        reviews_sort: str = self.request.GET.get('reviews_sort')
        purchase_sort: str = self.request.GET.get('purchase_sort')

        min_price = self.object_list.aggregate(Min('price'))['price__min']
        max_price = self.object_list.aggregate(Max('price'))['price__max']

        if not self.request.session.get('min_price') or not self.request.session.get('max_price'):
            self.request.session['min_price'] = str(min_price)
            self.request.session['max_price'] = str(max_price)
        else:
            min_price = self.request.session.get('min_price')
            max_price = self.request.session.get('max_price')

        if price_range:
            curr_min_price, curr_max_price = price_range.split(';')[0], price_range.split(';')[1]
            context['curr_min_price'], context['curr_max_price'] = curr_min_price, curr_max_price

        context['min_price'], context['max_price'] = min_price, max_price

        if category and category != 'all':
            context['category'] = category
        if title:
            context['title'] = title
        if in_stock:
            context['in_stock'] = True
        if delivery_free:
            context['delivery_free'] = True

        if price_sort:
            context['price_sort'] = price_sort
        if created_at_sort:
            context['created_at_sort'] = created_at_sort
        if reviews_sort:
            context['reviews_sort'] = reviews_sort
        if purchase_sort:
            context['purchase_sort'] = purchase_sort

        if price_sort or created_at_sort or reviews_sort:
            context['any_sort'] = True

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offers = Offer.objects.filter(product=self.object)
        context['offers'] = offers
        # добавляем форму для отзыва
        reviews = Review.objects.filter(offer__product=self.object, is_active=True)
        context['reviews'] = reviews
        # добавляем список продавцов для выбора в форме
        sellers = Seller.objects.filter(profile__in=[offer.seller.profile for offer in offers])
        context['sellers'] = sellers

        # создаём форму для отзыва
        if self.request.user.is_authenticated:
            form = ReviewForm()
            context['form'] = form
        return context

    # def post(self, request, pk):
    #     """ логика для добавления отзыва к товару """
    #     pass


def add_product_review(request):
    """ Вью для добавления отзыва к товару """
    if request.method == 'POST':
        review_service.new_review(request)
