from django.db import models
from django.core.validators import RegexValidator



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
    def number_default():
        if Round.objects.count() == 0:
            return 1
        else:
            return Round.objects.latest().number + 1
    
    number = models.PositiveIntegerField(default=number_default)
    scheduled_time = models.DateTimeField(blank=True, null=True, default=None, help_text="Used only for displaying purposes.")
    
    
    def __str__(self):
        return 'Round %d' % self.number
    
    class Meta:
        ordering = ['number']
        get_latest_by = 'number'



class Match(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team, through='TeamScore')
    table = models.ForeignKey(Table, on_delete=models.CASCADE, blank=True, null=True, default=None)
    
    def __str__(self):
        return 'Match %s' % ' - '.join(team.name for team in self.teams.all())


class TeamScore(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, default=None)
    
    class Meta:
        ordering = ['match__pk', 'team__name']


