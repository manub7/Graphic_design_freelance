# Generated by Django 3.2 on 2021-05-19 08:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_order_upload'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='upload',
        ),
    ]