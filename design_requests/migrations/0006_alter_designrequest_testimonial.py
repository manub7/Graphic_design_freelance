# Generated by Django 3.2 on 2021-05-29 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design_requests', '0005_designrequest_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='designrequest',
            name='testimonial',
            field=models.TextField(blank=True, null=True),
        ),
    ]