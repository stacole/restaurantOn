# Generated by Django 4.1.1 on 2022-11-12 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_order_tax_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='vendor',
            new_name='vendors',
        ),
        migrations.AlterField(
            model_name='order',
            name='bracelet',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]