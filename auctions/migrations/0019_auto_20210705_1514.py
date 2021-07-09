# Generated by Django 3.2.3 on 2021-07-05 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0018_auto_20210621_0440'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='zipcode',
            field=models.CharField(blank=True, max_length=10, verbose_name='Zip Code'),
        ),
        migrations.AlterField(
            model_name='address',
            name='country',
            field=models.CharField(max_length=64, verbose_name='Country'),
        ),
    ]