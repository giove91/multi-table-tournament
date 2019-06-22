# Generated by Django 2.1.9 on 2019-06-22 14:10

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import tournament.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('N', 'Normal'), ('B', 'Bye')], default='N', max_length=1)),
            ],
            options={
                'verbose_name_plural': 'matches',
                'ordering': ['round', '-type', 'pk'],
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(blank=True, max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('is_captain', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['team', 'name'],
            },
        ),
        migrations.CreateModel(
            name='PlayerResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.DecimalField(blank=True, decimal_places=1, default=None, max_digits=4, null=True)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournament.Match')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournament.Player')),
            ],
            options={
                'ordering': ['match', 'player'],
            },
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('visibility', models.CharField(choices=[('H', 'Hide'), ('R', 'Hide results'), ('S', 'Show')], default='S', max_length=2)),
                ('scheduled_time', models.DateTimeField(blank=True, default=None, help_text='Used only for displaying purposes.', null=True)),
            ],
            options={
                'ordering': ['number'],
                'get_latest_by': 'number',
            },
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('priority', models.IntegerField(default=100, help_text='A number between 0 and 100. Tables with higher priority are preferred when creating a new turn.', validators=[tournament.models.validate_priority])),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('active', models.BooleanField(default=True, help_text='Inactive teams are not considered for future turns and do not appear in the scoreboard.')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TeamResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.DecimalField(blank=True, decimal_places=1, default=None, max_digits=4, null=True)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournament.Match')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournament.Team')),
            ],
            options={
                'ordering': ['match', 'team'],
            },
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('bye_score', models.DecimalField(decimal_places=1, default=3, help_text='Score to assign for a bye.', max_digits=4)),
                ('default_round_visibility', models.CharField(choices=[('H', 'Hide'), ('R', 'Hide results'), ('S', 'Show')], default='S', help_text='Default visibility of newly generated rounds.', max_length=2)),
                ('shown_players', models.PositiveIntegerField(blank=True, default=0, help_text='Number of players to show in the scoreboard. If no value is given, all players are shown. If 0, the player scoreboard is not shown.', null=True)),
                ('is_registration_open', models.BooleanField(default=False)),
                ('max_teams', models.PositiveIntegerField(blank=True, default=None, help_text='Maximum number of allowed teams during registration. If no value is given, the number is unlimited.', null=True)),
            ],
            options={
                'ordering': ['creation_time'],
                'get_latest_by': 'creation_time',
            },
        ),
        migrations.AlterUniqueTogether(
            name='table',
            unique_together={('name',)},
        ),
        migrations.AddField(
            model_name='round',
            name='tournament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournament.Tournament'),
        ),
        migrations.AddField(
            model_name='player',
            name='team',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='tournament.Team'),
        ),
        migrations.AddField(
            model_name='match',
            name='players',
            field=models.ManyToManyField(through='tournament.PlayerResult', to='tournament.Player'),
        ),
        migrations.AddField(
            model_name='match',
            name='round',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournament.Round'),
        ),
        migrations.AddField(
            model_name='match',
            name='table',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tournament.Table'),
        ),
        migrations.AddField(
            model_name='match',
            name='teams',
            field=models.ManyToManyField(through='tournament.TeamResult', to='tournament.Team'),
        ),
    ]
