Liquibase migrations with django.
*********************************
License: BSD
Author:  Marek Wywiał <onjinx@gmail.com>


How it works
------------
Database settings are got from DATEBASES, from key 'default' or key
configured in settings.py as LIQUIMIGRATE_DATABASE.

Changelog path are got from LIQUIMIGRATE_CHANGELOG_FILE or from command line
(check -h).

Supported driver:
 * postgresql
 * mysql
 * more in future


Install
-------
 - install liquimigrate egg 
 - add 'liquimigrate' to INSTALLED_APPS
 - configure LIQUIMIGRATE_CHANGELOG_FILE os.path.join(os.path.dirname(__file__), "migrations", "your.xml") in settings
 - ensure that you have java on your path


Usage
-----
Just run ./management.py liquibase update or ./management.py liquibase -h


Development
-----------
Whole command code is put in:
 - liquimigrate/management/commands/liquibase.py
 - java connectors are put in liquimigrate/vendor/connectors
 - available drivers mapping is put in liquimigrate/__init__.py
 - mapping to create db url for drivers is stored in liquimigrate/management/commands/liquibase.py in  DB_DEFAULTS
