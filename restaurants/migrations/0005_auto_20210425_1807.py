# Generated by Django 3.1.8 on 2021-04-25 18:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0004_order_total'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mealrelations',
            old_name='meals',
            new_name='meal',
        ),
    ]