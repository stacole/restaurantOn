# Generated by Django 4.1.1 on 2022-11-19 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_rename_vendor_order_vendors_alter_order_bracelet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='bracelet',
        ),
        migrations.RemoveField(
            model_name='order',
            name='table',
        ),
    ]
