# Generated by Django 2.2.3 on 2019-07-25 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0005_auto_20190704_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='description',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
