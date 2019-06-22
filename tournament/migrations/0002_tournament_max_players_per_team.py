# Generated by Django 2.1.9 on 2019-06-22 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='max_players_per_team',
            field=models.PositiveIntegerField(blank=True, default=0, help_text='Maximum number of allowed players per team during registration. If no value is given, the number is unlimited.', null=True),
        ),
    ]
