Liquibase migrations with django.
*********************************
License: BSD
Liquibase license: Apache 2.0
Author:  Marek Wywiał <onjinx@gmail.com>


Quick start
-----------
 - install liquimigrate, python setup.py install
 - add 'liquimigrate' to **INSTALLED_APPS**
 - configure **LIQUIMIGRATE_CHANGELOG_FILES** = { 'default': os.path.join(os.path.dirname(__file__), "migrations", "migrations.xml") in settings }
 - ensure that you have java on your path, liquibase and java drivers are embedded into package


Usage
-----
Just run ./management.py liquibase update or ./management.py liquibase -h

To learn how to use liquibase look at liquibase documentation:
 * http://www.liquibase.org/quickstart


Configuration settings
----------------------
 * **LIQUIMIGRATE_CHANGELOG_FILES** - dictionary with paths to change log files f.e. 'os.path.join(os.path.dirname(__file__), "migrations", "migrations.xml")' for every database connection you need to maintain using liquimigrate
 * old method is still supported: **LIQUIMIGRATE_CHANGELOG_FILE** - path to change log file f.e. 'os.path.join(os.path.dirname(__file__), "migrations", "migrations.xml")'
 * **LIQUIMIGRATE_DATABASE** - selected database - default 'default'


How it works
------------
Database settings are got from **DATEBASES**, from key *'default'* or key
configured in settings.py as **LIQUIMIGRATE_DATABASE**.

Changelog path are got from **LIQUIMIGRATE_CHANGELOG_FILES** or from command line
(check -h).

Supported drivers:
 * postgresql
 * mysql
 * more in future


Development
-----------
Whole command code is put in:
 - liquimigrate/management/commands/liquibase.py
 - java connectors are stored in liquimigrate/vendor/connectors
 - available drivers mapping is stored in liquimigrate/__init__.py
 - mapping to create db url for drivers is stored in liquimigrate/management/commands/liquibase.py in **DB_DEFAULTS**
