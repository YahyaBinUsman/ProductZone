# Generated by Django 5.0.3 on 2024-04-21 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('keychain_app', '0015_rename_total_price_after_gst_order_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.CharField(max_length=100),
        ),
    ]
