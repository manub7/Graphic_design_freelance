# Generated by Django 3.2 on 2021-05-13 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20210512_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=13),
        ),
        migrations.AlterField(
            model_name='order',
            name='size',
            field=models.DecimalField(decimal_places=0, default=0, editable=False, max_digits=13),
        ),
    ]
