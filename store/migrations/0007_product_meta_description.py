# Generated by Django 5.1.5 on 2025-01-24 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='meta_description',
            field=models.CharField(blank=True, max_length=160),
        ),
    ]
