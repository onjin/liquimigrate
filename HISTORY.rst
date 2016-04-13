.. :changelog:

History
-------

0.5.2 (2015-10-22)
------------------

* added `management` to `MANIFEST.in`

0.5.1 (2015-10-22)
------------------

* handle liquibase return codes as an exception

0.5.0 (2015-08-06)
------------------

* add documentation and better package layout

0.4.1 (2015-08-06)
------------------

* fix for disabling signals
* add possiblity to disable emitting pre- and postmigrate signals
* add example project configured with liquibase migrations

0.4.0 (2014-09-28)
------------------

* more detailed messages in makemigrations and squashmigrations commands
* Django 1.7+ compatibility + wrapped migration commands

0.3.0 (2014-02-17)
------------------

* Update README.rst
* removed version from __init__
* Update README.rst
* back to previous versioning scheme
* cleaned up settings header
* Changed Makefile:pypi to not use iw.dist
* Update README.rst
* possibility to change liquibase jar and connectors via settings
* db name, host, port were overriden by defaults

0.2.8 (2012-02-28)
------------------

* Updated documentation about new LIQUIMIGRATE_CHANGELOG_FILES directive Renamed README.txt to README.rst & included into MANIFEST.in Print additional info only in --verbosity 1 model Minor changes for PEP8
* full multidb support

0.2.7 (2011-06-01)
------------------

* emit post_sync signal, call loaddata and initial_data
* support for singledb django versions
* fixed driver option

0.2.6 (2011-05-20)
------------------

* accepting --driver option from command line

0.2.5 (2011-05-18)
------------------

* Better README.txt - link to liquibase

0.2.4 (2011-05-17)
------------------

* FIXED: project path

0.2.3 (2011-05-17)
------------------

* Updated README.txt about mysql driver & about BSD license

0.2.2 (2011-05-17)
------------------

* ADDED: pass other args as liquibase args

0.2.1 (2011-05-17)
------------------

* FIXED: too small tuple when using not supported db driver

0.2.0 (2011-04-29)
------------------

* ADDED: mysql connector

0.1.2 (2011-04-28)
------------------

* ADDED: custom syncdb command
* ADDED: ensure command was given & more README.txt
* FIXED: run cmdline than just print them ;)
* FIXED: missing vendor in egg

0.1.1 (2011-04-28)
------------------

* REMOVED: old dependencies/namespaces

0.1.0 (2011-04-28)
------------------

