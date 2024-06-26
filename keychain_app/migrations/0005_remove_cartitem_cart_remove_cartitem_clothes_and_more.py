# Generated by Django 5.0.3 on 2024-03-17 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('keychain_app', '0004_remove_cart_user_cart_guest_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='clothes',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='keychain',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='wallet',
        ),
        migrations.RemoveField(
            model_name='clothes',
            name='cart_quantity',
        ),
        migrations.RemoveField(
            model_name='keychain',
            name='cart_quantity',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='cart_quantity',
        ),
        migrations.AlterField(
            model_name='clothes',
            name='image',
            field=models.ImageField(upload_to='clothes_images'),
        ),
        migrations.AlterField(
            model_name='clothes',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='keychain',
            name='image',
            field=models.ImageField(upload_to='keychain_images'),
        ),
        migrations.AlterField(
            model_name='keychain',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='image',
            field=models.ImageField(upload_to='wallet_images'),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]
