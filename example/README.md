Example liquimigrate project
----------------------------

This is an example django project with sample liquibase migrations.

Liquibase migrations can be used together with django syncdb/migrate but you need make sure that migrations does not
conflict with each other.


Install
-------

 $ git clone https://github.com/onjin/liquimigrate.git
 $ cd liquimigrate/example
 $ mkvirtualenv liquimigrateapp
 $ edit liquimigrateapp/settings.py  # and provide your DATABASES credentials
 $ ./manage.py syncdb  # to run initial django syncdb and migrations, confirm by typing 'yes'
 $ ./manage.py liquibase update  # to run migrations from migrations/migrations.xml
