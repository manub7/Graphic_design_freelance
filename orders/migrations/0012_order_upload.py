# Generated by Django 3.2 on 2021-05-18 08:22

from django.db import migrations, models
import orders.models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_auto_20210517_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='upload',
            field=models.FileField(null=True, upload_to=orders.models.order_directory_path),
        ),
    ]
