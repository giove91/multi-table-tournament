import os
import sys
import django
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a new round for the current tournament.')
    args = parser.parse_args()
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtt.settings')
    django.setup()
    
    from tournament.models import *
    
    tournament = Tournament.objects.latest()
    print("Tournament:", tournament)
    tournament.create_round()
