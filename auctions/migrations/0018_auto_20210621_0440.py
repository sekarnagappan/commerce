# Generated by Django 3.2.3 on 2021-06-21 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0017_listings_update_ts'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='update_ts',
            field=models.DateTimeField(auto_now=True, verbose_name='Update Timestamp'),
        ),
        migrations.AddField(
            model_name='bids',
            name='update_ts',
            field=models.DateTimeField(auto_now=True, verbose_name='Update Timestamp'),
        ),
        migrations.AddField(
            model_name='category',
            name='update_ts',
            field=models.DateTimeField(auto_now=True, verbose_name='Update Timestamp'),
        ),
        migrations.AddField(
            model_name='comments',
            name='update_ts',
            field=models.DateTimeField(auto_now=True, verbose_name='Update Timestamp'),
        ),
        migrations.AddField(
            model_name='watchlist',
            name='update_ts',
            field=models.DateTimeField(auto_now=True, verbose_name='Update Timestamp'),
        ),
    ]