# Generated by Django 3.1.1 on 2020-10-18 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_bid_category_comments_listing'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='current_bid',
            field=models.IntegerField(blank=True, default=-1),
            preserve_default=False,
        ),
    ]
