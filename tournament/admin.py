from django.contrib import admin
from .models import *


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'creation_time')
    search_fields = ('name',)



class PlayerInline(admin.TabularInline):
    model = Player

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = (PlayerInline,)
    list_display = ('name', 'players')
    search_fields = ('name',)
    
    def players(self, obj):
        return ", ".join(player.name for player in obj.player_set.all())


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'phone_number', 'is_captain')
    # list_editable = ('team', 'phone_number', 'is_captain')
    
    search_fields = ('name', 'team__name')
    autocomplete_fields = ('team',)


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority')
    list_editable = ('priority',)

    search_fields = ('name',)


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'scheduled_time',)



class TeamScoreInline(admin.TabularInline):
    model = TeamScore
    verbose_name_plural = 'teams'
    max_num = 2
    extra = 2

class PlayerScoreInline(admin.TabularInline):
    model = PlayerScore
    verbose_name_plural = 'players'
    extra = 0

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    inlines = (TeamScoreInline, PlayerScoreInline)
    list_display = ('__str__', 'round', 'table',)
    list_filter = ('round', 'table',)
    autocomplete_fields = ('players',)


