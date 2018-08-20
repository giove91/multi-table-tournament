# Generated by Django 2.1 on 2018-08-20 19:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0002_tournament_bye_score'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='match',
            options={'ordering': ['round', '-type', 'pk'], 'verbose_name_plural': 'matches'},
        ),
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': ['team', 'name']},
        ),
        migrations.AlterOrderWithRespectTo(
            name='player',
            order_with_respect_to=None,
        ),
    ]