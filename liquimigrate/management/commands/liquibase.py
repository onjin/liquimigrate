from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from liquimigrate import LIQUIBASE_JAR, LIQUIBASE_DRIVERS
from optparse import make_option
import os
        
DB_DEFAULTS = {
    'postgresql': {
        'tag': 'postgresql',
        'host': 'localhost',
        'port': 5432,
    },
    'mysql': {
        'tag': 'mysql',
        'host': 'localhost',
        'port': 3306,
    },
}

class Command(BaseCommand):
    help = "liquibase migrations"

    option_list = BaseCommand.option_list + (
        make_option('', '--changeLogFile', dest='changelog_file',
            help='XML file with changelog'),
        make_option('', '--driver', dest='driver',
            help='db driver'),
        make_option('', '--username', dest='username',
            help='db username'),
        make_option('', '--password', dest='password',
            help='db password'),
        make_option('', '--url', dest='url',
            help='db url'),
        )

    def handle(self, *args, **options):
        """
        Handle liquibase command parameters
        """
        try:
            database = settings.LIQUIMIGRATE_DATABASE
        except AttributeError:
            database = 'default'

        dbsettings = settings.DATABASES[database]

        # get driver
        driver_class = options.get('driver', dbsettings.get('ENGINE').split('.')[-1])
        dbtag, driver, classpath = LIQUIBASE_DRIVERS.get(driver_class, ( None, None, None))
        if driver is None:
            raise CommandError("unsupported db driver '%s'\navailable drivers: %s" % (driver_class, ' '.join(LIQUIBASE_DRIVERS.keys())))

        # command options 
        changelog_file = options.get('changelog_file') or settings.LIQUIMIGRATE_CHANGELOG_FILE
        username = options.get('username') or  dbsettings.get('USER')
        password = options.get('password') or  dbsettings.get('PASSWORD')
        url = options.get('url') or _get_url_for_db(dbtag, dbsettings)

        if len(args) < 1:
            raise CommandError("give me any command, for example 'update'")

        command = args[0]
        cmdargs = {
            'jar': LIQUIBASE_JAR,
            'changelog_file': changelog_file,
            'username': username,
            'password': password,
            'command': command,
            'driver': driver,
            'classpath': classpath,
            'url': url,
            'args': ' '.join(args[1:]),
        }

        cmdline = "java -jar %(jar)s --changeLogFile %(changelog_file)s \
--username=%(username)s --password=%(password)s \
--driver=%(driver)s --classpath=%(classpath)s --url=%(url)s \
%(command)s %(args)s" % ( cmdargs)

        print "executing: %s" % (cmdline,)
        os.system( cmdline)


def _get_url_for_db(tag, dbsettings):
    pattern = "jdbc:%(tag)s://%(host)s:%(port)s/%(name)s"
    options = {
            'name': dbsettings.get('NAME', ''),
            'host': dbsettings.get('HOST', ''),
            'port': dbsettings.get('PORT', ''),
    }
    options.update( DB_DEFAULTS.get(tag))
    return pattern %  options 

