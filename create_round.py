import os
import sys
import django
import argparse


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtt.settings')
    django.setup()
    
    from tournament.models import *
    
    tournament = Tournament.objects.latest()
    print(tournament)
    tournament.create_round()
