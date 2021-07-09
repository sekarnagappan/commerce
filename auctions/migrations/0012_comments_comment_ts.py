# Generated by Django 3.2.3 on 2021-06-15 04:26

from django.db import migrations, models
from datetime import date

class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_alter_listings_short_desc'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='comment_ts',
            field=models.DateTimeField(auto_now_add=True, default=date.today, verbose_name='Comment Timestamp'),
            preserve_default=False,
        ),
    ]
