# Generated by Django 4.1.1 on 2022-11-26 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_remove_order_bracelet_remove_order_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='bracelet',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='table',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
