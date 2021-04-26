# Generated by Django 3.1.8 on 2021-04-25 17:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0002_auto_20210425_1721'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='restaurant_owner',
        ),
        migrations.AddField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='orders_restaurant', to='restaurants.restaurant', verbose_name='Restaurant'),
            preserve_default=False,
        ),
    ]