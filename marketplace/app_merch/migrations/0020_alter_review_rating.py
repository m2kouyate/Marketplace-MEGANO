# Generated by Django 3.2.18 on 2023-06-06 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_merch', '0019_discount_set_of_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.PositiveIntegerField(help_text='Введите рейтинг от 1 до 5', verbose_name='Рейтинг'),
        ),
    ]
