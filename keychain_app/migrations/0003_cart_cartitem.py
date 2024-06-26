# Generated by Django 5.0.3 on 2024-03-17 12:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('keychain_app', '0002_clothes_cart_quantity_keychain_cart_quantity_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='keychain_app.cart')),
                ('clothes', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='keychain_app.clothes')),
                ('keychain', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='keychain_app.keychain')),
                ('wallet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='keychain_app.wallet')),
            ],
        ),
    ]
