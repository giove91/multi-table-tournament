import os
import sys
import django
import argparse


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtt.settings')
    django.setup()
    
    from tournament.models import *
    
    if len(sys.argv) < 2:
        print("Error: specify the name of the tournament")
        sys.exit()
    
    tournament = Tournament.objects.create(name=' '.join(sys.argv[1:]))
    print("Tournament:", tournament)
