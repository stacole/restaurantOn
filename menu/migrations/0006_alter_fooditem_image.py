# Generated by Django 4.1.1 on 2022-12-03 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0005_alter_fooditem_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fooditem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='foodimages'),
        ),
    ]
