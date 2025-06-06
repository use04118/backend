# Generated by Django 5.1.6 on 2025-06-02 11:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_role_created_at_role_is_permanently_removed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='business',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.business'),
        ),
        migrations.AlterField(
            model_name='role',
            name='role_name',
            field=models.CharField(choices=[('admin', 'Admin'), ('salesman', 'Salesman'), ('delivery_boy', 'Delivery Boy'), ('stock_manager', 'Stock Manager'), ('partner', 'Partner'), ('accountant', 'Accountant')], max_length=30),
        ),
        migrations.AlterField(
            model_name='role',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='staffinvite',
            name='role_name',
            field=models.CharField(choices=[('admin', 'Admin'), ('salesman', 'Salesman'), ('delivery_boy', 'Delivery Boy'), ('stock_manager', 'Stock Manager'), ('partner', 'Partner'), ('accountant', 'Accountant')], max_length=30),
        ),
    ]
