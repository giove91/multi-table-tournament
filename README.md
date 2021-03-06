# Multi-table Tournament
Web application to manage a Swiss-like tournament where matches are played at different tables, and every team should play at most once at every table.


## Local testing

To run the application locally: clone the repository, install the [requirements](requirements.txt) (Python 3 is needed), and then issue the following commands.

```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

From now on, everything can be done from the web interface, on the `/admin/` page.
However, you can also use the following command-line scripts to populate the database.

- `python create_tournament.py NAME` Create a tournament with the given name.
- `python generate_data.py NUM_TEAMS NUM_PLAYERS NUM_TABLES` Generate `NUM_TEAMS` teams, each having `NUM_PLAYERS` players, and also generate `NUM_TABLES` tables.
- `python create_round.py` Create a new round for the latest tournament (uses teams and tables already present in the database, as well as previous rounds).
- `python generate_results.py` Generate random results for all existing matches.

The public page (with rounds and scoreboard) is available at `/`.
