# Generated by Django 2.1 on 2018-08-20 19:30

from django.db import migrations, models
import tournament.models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0003_auto_20180820_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='priority',
            field=models.IntegerField(default=100, help_text='A number between 0 and 100. Tables with higher priority are preferred when creating a new turn.', validators=[tournament.models.validate_priority]),
        ),
    ]