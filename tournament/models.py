from django.db import models
from django.core.validators import RegexValidator


class Tournament(models.Model):
    name = models.CharField(max_length=1024)
    creation_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['creation_time']
        get_latest_by = 'creation_time'



class Team(models.Model):
    name = models.CharField(max_length=1024)
    active = models.BooleanField(default=True, help_text='Inactive teams are not considered for future turns and do not appear in the scoreboard.')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    


class Player(models.Model):
    name = models.CharField(max_length=256)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True, default=None)
    
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    is_captain = models.BooleanField(default=False)
    
    
    def __str__(self):
        return '%s (%s)' % (self.name, self.team.name)
    
    class Meta:
        order_with_respect_to = 'team'



class Table(models.Model):
    name = models.CharField(max_length=256)
    priority = models.IntegerField(default=100, help_text='Tables with higher priority are preferred when creating a new turn.')
    

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = ('name',)



class Round(models.Model):
    number = models.PositiveIntegerField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField(blank=True, null=True, default=None, help_text="Used only for displaying purposes.")
    
    
    def __str__(self):
        return 'Round %d' % self.number
    
    class Meta:
        ordering = ['number']
        get_latest_by = 'number'



class Match(models.Model):
    NORMAL = 'N'
    BYE = 'B'
    TYPE_CHOICES = ((NORMAL, 'Normal'), (BYE, 'Bye'))
    
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=NORMAL)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, blank=True, null=True, default=None)
    teams = models.ManyToManyField(Team, through='TeamScore')
    players = models.ManyToManyField(Player, through='PlayerScore')
    
    def __str__(self):
        return ' - '.join(team.name for team in self.teams.all()) if self.teams.count() > 0 else 'Empty match'
    
    class Meta:
        ordering = ['round', 'type', 'pk']
        verbose_name_plural = 'matches'


class TeamScore(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, default=None)
    
    class Meta:
        ordering = ['match', 'team']


class PlayerScore(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, default=None)
    
    class Meta:
        ordering = ['match', 'player']


