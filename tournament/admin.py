from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group

# from django.contrib.auth.admin import UserAdmin

from django_object_actions import DjangoObjectActions # https://github.com/crccheck/django-object-actions

from .models import *


class MTTAdminSite(AdminSite):
    site_header = 'Multi-table tournament administration'
    site_title = 'MTT admin'
    index_template = 'admin_index.html'
    # app_index_template = 'admin_app_index.html'

admin_site = MTTAdminSite(name='mttadmin')

# admin_site.register(User)
# admin_site.register(Group)


# @admin.register(User, site=admin_site)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'is_active', 'is_staff', 'is_superuser')
#     fields = ('username', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')


@admin.register(Tournament, site=admin_site)
class TournamentAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('name', 'creation_time', 'bye_score', 'shown_players', 'is_registration_open', 'max_teams', 'max_players_per_team', 'num_rounds')
    # list_display = ('name', 'creation_time', 'bye_score', 'shown_players', 'num_rounds', 'team_scores', 'player_scores')
    search_fields = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'short_name', 'bye_score')
        }),
        ('Public page', {
            'fields': ('description', 'default_round_visibility', 'shown_players'),
        }),
        ('Registration', {
            'fields': ('is_registration_open', 'max_teams', 'max_players_per_team'),
        }),
    )

    def create_round(self, request, obj):
        round, success = obj.create_round()
        if not success:
            self.message_user(
                request,
                format_html('<a href="%s">Round %d</a> created, but not all teams could be paired.' % (reverse('admin:tournament_round_change', args=(round.id,)), round.number)),
                level=messages.WARNING
            )
        else:
            self.message_user(
                request,
                format_html('<a href="%s">Round %d</a> created.' % (reverse('admin:tournament_round_change', args=(round.id,)), round.number)),
                level=messages.SUCCESS
            )

    create_round.label = "Generate round"
    create_round.short_description = "Generate a new round with matches"

    change_actions = ('create_round',)

    def team_scores(self, obj):
        return score_counter_to_str(obj.team_scoreboard())

    def player_scores(self, obj):
        return score_counter_to_str(obj.player_scoreboard(), hide_secondary=True)




class PlayerInline(admin.TabularInline):
    model = Player

@admin.register(Team, site=admin_site)
class TeamAdmin(admin.ModelAdmin):
    inlines = (PlayerInline,)
    list_display = ('name', 'active', 'players')
    search_fields = ('name',)
    list_filter = ('active',)

    def players(self, obj):
        return ", ".join(player.name for player in obj.player_set.all())


@admin.register(Player, site=admin_site)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', '_active', 'phone_number', 'is_captain')
    list_filter = ('team', 'team__active')
    # list_editable = ('team', 'phone_number', 'is_captain')

    search_fields = ('name', 'team__name')
    autocomplete_fields = ('team',)


@admin.register(Table, site=admin_site)
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'description', 'num_matches')
    list_editable = ('priority',)

    search_fields = ('name',)


class TeamResultInline(admin.TabularInline):
    model = TeamResult
    verbose_name_plural = 'teams'
    autocomplete_fields = ('team',)
    # TODO: limit teams to those that are not already in a match
    # (Django 2.1 does not support this together with autocomplete_fields)

    max_num = 2
    extra = 2

class PlayerResultInline(admin.TabularInline):
    model = PlayerResult
    verbose_name_plural = 'players'
    autocomplete_fields = ('player',)
    extra = 0
    can_delete = False

@admin.register(Match, site=admin_site)
class MatchAdmin(admin.ModelAdmin):
    inlines = (TeamResultInline, PlayerResultInline)
    # list_display = ('__str__', 'show_round', 'type', 'valid', 'table', 'result', 'team_scores', 'player_scores')
    list_display = ('__str__', 'show_round', 'type', 'valid', 'table', 'result')
    list_filter = ('round__tournament', 'round', 'table', 'type')

    def show_round(self, obj):
        return format_html("<a href='{url}'>{round}</a>", url=reverse('admin:tournament_round_change', args=(obj.round.id,)), round=obj.round)
    show_round.short_description = "round"

    def team_scores(self, obj):
        return score_counter_to_str(obj.team_scoreboard())

    def player_scores(self, obj):
        return score_counter_to_str(obj.player_scoreboard(), hide_secondary=True)


class MatchInline(admin.TabularInline):
    model = Match
    extra = 0
    # fields = ('type', 'table',)
    show_change_link = True
    # inlines = (TeamResultInline)


@admin.register(Round, site=admin_site)
class RoundAdmin(DjangoObjectActions, admin.ModelAdmin):
    # list_display = ('__str__', 'tournament', 'visibility', 'scheduled_time', 'num_matches', 'completed_matches', 'team_scores')
    list_display = ('__str__', 'tournament', 'visibility', 'scheduled_time', 'num_matches', 'completed_matches')
    list_filter = ('tournament',)
    inlines = (MatchInline,)

    def view_matches(self, request, obj):
        return HttpResponseRedirect(reverse('admin:tournament_match_changelist') + '?round__id__exact=%d' % obj.id)

    view_matches.label = "View matches"
    view_matches.short_description = "View list of matches of this round"

    change_actions = ('view_matches',)

    def team_scores(self, obj):
        return score_counter_to_str(obj.team_scoreboard())
