# Generated by Django 5.0.3 on 2024-04-21 18:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('keychain_app', '0016_alter_order_payment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='total_price',
            new_name='total_price_after_gst',
        ),
    ]
