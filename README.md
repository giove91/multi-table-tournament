# Multi-table Tournament
Web application to manage a Swiss-like tournament where matches are played at different tables, and every team should play at most once at every table.


## Requirements

* Python 3
* [Django 2.1](https://docs.djangoproject.com/en/2.1/)
* [NetworkX 2.1](https://networkx.github.io)
* [Django-object-actions](https://github.com/crccheck/django-object-actions)


## Local testing

To run the application locally, clone the repository and then issue the following commands.

```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
