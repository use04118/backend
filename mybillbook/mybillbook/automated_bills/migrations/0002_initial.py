# Generated by Django 5.1.6 on 2025-05-31 11:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('automated_bills', '0001_initial'),
        ('inventory', '0001_initial'),
        ('parties', '0001_initial'),
        ('sales', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='automatedinvoice',
            name='business',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='automatedinvoices', to='users.business'),
        ),
        migrations.AddField(
            model_name='automatedinvoice',
            name='party',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parties.party'),
        ),
        migrations.AddField(
            model_name='automatedinvoice',
            name='tcs',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.tcs'),
        ),
        migrations.AddField(
            model_name='automatedinvoiceitem',
            name='automatedinvoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='automatedinvoice_items', to='automated_bills.automatedinvoice'),
        ),
        migrations.AddField(
            model_name='automatedinvoiceitem',
            name='gstTaxRate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.gsttaxrate'),
        ),
        migrations.AddField(
            model_name='automatedinvoiceitem',
            name='item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.item'),
        ),
        migrations.AddField(
            model_name='automatedinvoiceitem',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.service'),
        ),
    ]
