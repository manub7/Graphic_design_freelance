# Generated by Django 3.2 on 2021-05-12 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(editable=False, max_length=32)),
                ('name', models.CharField(max_length=254)),
                ('description', models.TextField()),
                ('height', models.DecimalField(decimal_places=0, max_digits=6)),
                ('width', models.DecimalField(decimal_places=0, max_digits=6)),
                ('size', models.DecimalField(decimal_places=0, max_digits=6)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('provide_source_files', models.BooleanField(default=False)),
                ('source_img', models.ImageField(blank=True, null=True, upload_to='')),
                ('processed_image', models.ImageField(blank=True, null=True, upload_to='')),
                ('is_processed', models.BooleanField(default=False)),
                ('testimonial', models.TextField()),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.category')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='profiles.client')),
            ],
        ),
    ]
