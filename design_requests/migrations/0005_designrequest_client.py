# Generated by Django 3.2 on 2021-05-24 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_auto_20210517_1356'),
        ('design_requests', '0004_alter_designrequest_order_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='designrequest',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_design_request', to='profiles.client'),
        ),
    ]
