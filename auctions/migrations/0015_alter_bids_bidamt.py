# Generated by Django 3.2.3 on 2021-06-19 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_auto_20210619_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bids',
            name='bidamt',
            field=models.FloatField(default=0.0, help_text='What is your bid? Must be higher then the highest bid.', verbose_name='Bib Price'),
        ),
    ]