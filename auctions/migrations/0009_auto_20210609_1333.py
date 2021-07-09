# Generated by Django 3.2.3 on 2021-06-09 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_auto_20210606_1321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listings',
            name='long_desc',
        ),
        migrations.AddField(
            model_name='listings',
            name='details',
            field=models.TextField(default='', help_text='Details', verbose_name='Details'),
            preserve_default=False,
        ),
    ]