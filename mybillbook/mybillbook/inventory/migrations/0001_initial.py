# Generated by Django 5.1.6 on 2025-05-31 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GSTTaxRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('cess_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('description', models.CharField(default='No description provided', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('itemName', models.CharField(max_length=255)),
                ('itemType', models.CharField(choices=[('Product', 'Product')], default='Product', max_length=10)),
                ('salesPrice', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('salesPriceType', models.CharField(choices=[('With Tax', 'With Tax'), ('Without Tax', 'Without Tax')], default='With Tax', max_length=50)),
                ('purchasePrice', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('purchasePriceType', models.CharField(choices=[('With Tax', 'With Tax'), ('Without Tax', 'Without Tax')], default='With Tax', max_length=50)),
                ('itemCode', models.CharField(max_length=100)),
                ('openingStock', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('closingStock', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('date', models.DateField()),
                ('itemBatch', models.CharField(blank=True, max_length=50, null=True)),
                ('enableLowStockWarning', models.BooleanField(blank=True, default=False, null=True)),
                ('lowStockQty', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('item_image', models.ImageField(blank=True, null=True, upload_to='static/images/')),
                ('description', models.TextField(blank=True, null=True)),
                ('hsnCode', models.CharField(blank=True, max_length=15, null=True)),
                ('created_at', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MeasuringUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serviceName', models.CharField(max_length=255)),
                ('serviceType', models.CharField(choices=[('Service', 'Service')], default='Service', max_length=10)),
                ('salesPrice', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('salesPriceType', models.CharField(choices=[('With Tax', 'With Tax'), ('Without Tax', 'Without Tax')], default='With Tax', max_length=50)),
                ('sacCode', models.CharField(blank=True, max_length=15, null=True)),
                ('serviceCode', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
