# Generated by Django 3.2 on 2021-05-16 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_alter_order_testimonial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='testimonial',
            field=models.TextField(blank=True, default=False, null=True),
        ),
    ]
