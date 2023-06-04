# Generated by Django 3.2.18 on 2023-06-02 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_users', '0020_auto_20230602_0656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('awaiting_payment', 'Ожидает оплаты'), ('delivered', 'Доставлен'), ('is_delivering', 'Доставляется')], max_length=20, null=True, verbose_name='статус доставки'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('paid', 'Оплачен'), ('not_paid', 'Не оплачен')], max_length=20, verbose_name='статус оплаты'),
        ),
    ]
