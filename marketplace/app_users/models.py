from app_merch.models import Offer, Product
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models


class Profile(models.Model):
    """
    Модель профиля пользователя.
    """
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='user',
                                db_index=True, verbose_name='пользователь')
    full_name = models.CharField(max_length=150, verbose_name='полное имя')
    phone_number = models.CharField(max_length=50, verbose_name='номер телефона')
    address = models.CharField(max_length=255, verbose_name='адрес')
    avatar = models.ForeignKey('app_merch.Image', on_delete=models.SET_NULL, related_name='profile',
                               blank=True, null=True, verbose_name='аватар')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.full_name


class Seller(models.Model):
    """
    Модель продавца.
    """
    profile = models.OneToOneField(Profile, on_delete=models.PROTECT, related_name='seller',
                                   db_index=True, verbose_name='профиль')
    title = models.CharField(max_length=100, verbose_name='название')
    description = models.TextField(max_length=1000, verbose_name='описание')

    class Meta:
        verbose_name = 'Продавец'
        verbose_name_plural = 'Продавцы'

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        Сброс кеша при изменении продавца.
        """
        if cache.get(f'Seller {self.pk} top products'):
            cache.delete(f'Seller {self.pk} top products')
        super().save()

    def delete(self, using=None, keep_parents=False):
        """
        Сброс кеша при удалении продавца.
        """
        if cache.get(f'Seller {self.pk} top products'):
            cache.delete(f'Seller {self.pk} top products')
        super().delete()


class Buyer(models.Model):
    """
    Модель покупателя.
    """
    profile = models.OneToOneField(Profile, null=True,  on_delete=models.PROTECT, related_name='profile',
                                   db_index=True, verbose_name='покупатель')
    views = models.ManyToManyField('app_merch.Product', verbose_name='история просмотров')

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'

    def __str__(self):
        return f'{self.profile}'


class ComparisonList(models.Model):
    """
    Модель для списка сравнения продуктов.
    """
    profile = models.OneToOneField(Buyer, null=True,  on_delete=models.PROTECT, related_name='compare',
                                   db_index=True, verbose_name='владелец списка')
    offer = models.ForeignKey('app_merch.Offer', null=True, on_delete=models.PROTECT, related_name='offer',
                              db_index=True, verbose_name='список для сравнения')

    class Meta:
        verbose_name = 'Список сравнения'
        verbose_name_plural = 'Списки сравнения'

    def add_to_list(self):
        pass

    def remove_from_list(self):
        pass

    def return_list(self):
        pass

    def return_amount_in_list(self):
        pass

    def __str__(self):
        return f'Список сравнения {self.profile}'
