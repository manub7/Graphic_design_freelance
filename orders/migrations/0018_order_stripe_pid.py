# Generated by Django 3.2 on 2021-05-25 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0017_order_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='stripe_pid',
            field=models.CharField(default='', max_length=254),
        ),
    ]