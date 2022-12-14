# Generated by Django 4.1.1 on 2022-11-12 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0005_alter_openinghour_options_and_more'),
        ('orders', '0003_orderedmenu_bracelet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderedmenu',
            name='bracelet',
        ),
        migrations.RemoveField(
            model_name='orderedmenu',
            name='table',
        ),
        migrations.AddField(
            model_name='order',
            name='bracelet',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='table',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='total_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='vendor',
            field=models.ManyToManyField(blank=True, to='vendor.vendor'),
        ),
    ]
