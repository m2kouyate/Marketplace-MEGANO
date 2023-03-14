# Generated by Django 3.2.18 on 2023-03-13 07:18

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app_merch', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='наименование')),
                ('slug', models.SlugField(unique=True, verbose_name='url')),
                ('is_active', models.BooleanField(default=True, verbose_name='активная категория')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('icon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_merch.image', verbose_name='иконка категории')),
                ('parent', mptt.fields.TreeForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='app_merch.category', verbose_name='родительская категория')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
            },
        ),
    ]
