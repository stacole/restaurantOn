# Generated by Django 4.1.1 on 2022-10-19 23:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0002_alter_menurestaurant_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fooditem',
            name='menu',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fooditems', to='menu.menurestaurant'),
        ),
    ]
