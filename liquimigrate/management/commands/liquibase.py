import distutils
import django
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from ...settings import LIQUIBASE_JAR, LIQUIBASE_DRIVERS
from ... import changesets


try:
    # Django 3.7
    from django.core.management.sql import (
            emit_pre_migrate_signal, emit_post_migrate_signal)
    emit_post_sync_signal = None
except ImportError:
    # Django 1.6 and older
    from django.core.management.sql import emit_post_sync_signal
    emit_pre_migrate_signal = None
    emit_post_migrate_signal = None


django_19_or_newer = (
        distutils.version.StrictVersion(django.__version__) >= '1.9')

try:
    from django.db import connections
    databases = connections.databases
except ImportError:
    # django without multidb support
    databases = {
            'default': {
                'ENGINE': settings.DATABASE_ENGINE,
                'HOST': settings.DATABASE_HOST,
                'PORT': settings.DATABASE_PORT,
                'NAME': settings.DATABASE_NAME,
                'USER': settings.DATABASE_USER,
                'PASSWORD': settings.DATABASE_PASSWORD,
            },
        }


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

    def add_arguments(self, parser):
        parser.add_argument('command', help='Liquibase command')
        parser.add_argument(
                'args', nargs='*', help='Liquibase positional arguments')
        parser.add_argument(
            '--changeLogFile', dest='changelog_file',
            help='XML file with changelog')
        parser.add_argument(
            '--driver', dest='driver',
            help='db driver')
        parser.add_argument(
            '--classpath', dest='classpath',
            help='jdbc driver class path')
        parser.add_argument(
            '--username', dest='username',
            help='db username')
        parser.add_argument(
            '--password', dest='password',
            help='db password')
        parser.add_argument('--url', dest='url', help='db url')
        parser.add_argument(
            '--database', dest='database', default='default',
            help='django database connection name')
        parser.add_argument(
            '-n', '--nosignals', dest='no_signals', action='store_true',
            default=False,
            help='disable emitting pre- and post migration signals')

    def handle(self, *args, **options):
        """
        Handle liquibase command parameters
        """
        database = getattr(
                settings, 'LIQUIMIGRATE_DATABASE', options['database'])

        try:
            dbsettings = databases[database]
        except KeyError:
            raise CommandError("don't know such a connection: %s" % database)

        verbosity = int(options.get('verbosity'))

        # get driver
        driver_class = (
                options.get('driver')
                or dbsettings.get('ENGINE').split('.')[-1])
        dbtag, driver, classpath = LIQUIBASE_DRIVERS.get(
                            driver_class, (None, None, None))

        classpath = options.get('classpath') or classpath

        if driver is None:
            raise CommandError(
                "unsupported db driver '%s'\n"
                "available drivers: %s" % (
                    driver_class, ' '.join(LIQUIBASE_DRIVERS.keys())))

        # command options
        changelog_file = (
                options.get('changelog_file')
                or _get_changelog_file(options['database']))
        username = options.get('username') or dbsettings.get('USER') or ''
        password = options.get('password') or dbsettings.get('PASSWORD') or ''
        url = options.get('url') or _get_url_for_db(dbtag, dbsettings)

        command = options['command']
        cmdargs = {
            'jar': LIQUIBASE_JAR,
            'changelog_file': changelog_file,
            'username': username,
            'password': password,
            'command': command,
            'driver': driver,
            'classpath': classpath,
            'url': url,
            'args': ' '.join(args),
        }

        cmdline = "java -jar %(jar)s --changeLogFile %(changelog_file)s \
--username=%(username)s --password=%(password)s \
--driver=%(driver)s --classpath=%(classpath)s --url=%(url)s \
%(command)s %(args)s" % (cmdargs)

        if verbosity > 0:
            print("changelog file: %s" % (changelog_file,))
            print("executing: %s" % (cmdline,))

        created_models = None   # we dont know it

        if emit_pre_migrate_signal and not options.get('no_signals'):
            if django_19_or_newer:
                emit_pre_migrate_signal(
                        1, options.get('interactive'), database)
            else:
                emit_pre_migrate_signal(
                    created_models, 1, options.get('interactive'), database)

        rc = os.system(cmdline)

        if rc == 0:

            try:
                if not options.get('no_signals'):
                    if emit_post_migrate_signal:
                        if django_19_or_newer:
                            emit_post_migrate_signal(
                                0, options.get('interactive'), database)
                        else:
                            emit_post_migrate_signal(
                                created_models, 0,
                                options.get('interactive'), database)
                    elif emit_post_sync_signal:
                        emit_post_sync_signal(
                                created_models, 0,
                                options.get('interactive'), database)

                if not django_19_or_newer:
                    call_command(
                        'loaddata', 'initial_data', verbosity=1,
                        database=database)
            except TypeError:
                # singledb (1.1 and older)
                emit_post_sync_signal(
                        created_models, 0, options.get('interactive'))

                call_command(
                        'loaddata', 'initial_data', verbosity=0)
        else:
            raise CommandError('Liquibase returned an error code %s' % rc)


def _get_url_for_db(tag, dbsettings):
    pattern = "jdbc:%(tag)s://%(host)s:%(port)s/%(name)s"
    options = dict(DB_DEFAULTS.get(tag))
    settings_map = {
        'NAME': 'name',
        'HOST': 'host',
        'PORT': 'port',
        }
    for key in settings_map:
        value = dbsettings.get(key)
        if value:
            options[settings_map[key]] = value

    return pattern % options


def _get_changelog_file(database):
    try:
        return changesets.get_changelog_file_for_database(database)
    except changesets.ImproperlyConfigured as ex:
        raise CommandError(ex)
