from django.db import models
from django.urls import reverse
from mptt.models import TreeForeignKey, MPTTModel
from app_users.models import Saller


class Image(models.Model):
    """ Модель картинок. """
    file = models.FileField(upload_to='static/assets/img/icons/', verbose_name='файл')
    title = models.CharField(max_length=150, verbose_name='наименование')

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'

    def __str__(self):
        return f'{self.pk}. {self.title}'


class Category(MPTTModel):
    """ Модель категории товаров. """
    title = models.CharField(max_length=150, verbose_name='наименование')
    icon = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='иконка категории'
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        verbose_name='родительская категория'
    )
    slug = models.SlugField(unique=True, verbose_name='url')
    is_active = models.BooleanField(default=True, verbose_name='активная категория')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    class MPTTMeta:
        order_insertion_by = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('categories_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    """
    Модель тэгов.
    """
    title = models.CharField(max_length=100, verbose_name='название')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.title


class Product(models.Model):
    """
    Модель продуктов.
    """
    title = models.CharField(max_length=150, verbose_name='название')
    description = models.TextField(max_length=1000, verbose_name='описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        db_index=True,
        verbose_name='категория'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='products',
        db_index=True,
        verbose_name='тэги'
    )
    icon = models.ForeignKey(
        Image,
        related_name='products',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='изображение продукта'
    )
    media = models.ManyToManyField(
        Image,
        verbose_name='медиафайлы продукта'
    )
    characters = models.JSONField(verbose_name='характеристики')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.title


class Offer(models.Model):
    """
    Модель предложений.
    """
    saller = models.ForeignKey(
        Saller,
        on_delete=models.PROTECT,
        related_name='offers',
        db_index=True,
        verbose_name='продавец'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='offers',
        db_index=True,
        verbose_name='продукт'
    )
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='цена')
    quantity = models.PositiveIntegerField(default=0, verbose_name='количество')
    is_active = models.BooleanField(default=True, verbose_name='актуальность')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')

    class Meta:
        verbose_name = 'Предложение'
        verbose_name_plural = 'Предложения'

    def __str__(self):
        return f"{self.product} from {self.saller}"


class Discount(models.Model):
    """
    Модель скидок.
    """
    offer = models.OneToOneField(
        Offer,
        on_delete=models.PROTECT,
        related_name='discounts',
        db_index=True,
        verbose_name='предложение'
    )
    is_percent = models.BooleanField(verbose_name='в процентах')
    size = models.PositiveIntegerField(verbose_name='размер')
    start_date = models.DateTimeField(verbose_name='дата начала')
    end_date = models.DateTimeField(verbose_name='дата окончания')
    description = models.TextField(max_length=1000, verbose_name='описание')
    is_active = models.BooleanField(default=True, verbose_name='актуальность')

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'

    def __str__(self):
        return f"Discount for {self.offer}"


class Banner(models.Model):
    """ Модель баннеров. """
    title = models.CharField(max_length=30, verbose_name='наименование')
    description = models.TextField(max_length=250, verbose_name='описание')
    file = models.ForeignKey(Image, on_delete=models.CASCADE, verbose_name='медиа файл')
    is_active = models.BooleanField(default=True, verbose_name='активность')
    link = models.URLField(verbose_name='ссылка')

    class Meta:
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'

    def __str__(self):
        return self.title
