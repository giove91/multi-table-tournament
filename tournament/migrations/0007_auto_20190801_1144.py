# Generated by Django 2.2.3 on 2019-08-01 09:44

from django.db import migrations, models
import tournament.models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0006_table_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='player_scoreboard_description',
            field=models.TextField(blank=True, default=None, help_text='This appears at the beginning of the player scoreboard. You can use HTML tags.', null=True),
        ),
        migrations.AlterField(
            model_name='table',
            name='priority',
            field=models.IntegerField(default=50, help_text='A number between 0 and 100. Tables with higher priority are preferred when creating a new turn.', validators=[tournament.models.validate_priority]),
        ),
    ]
