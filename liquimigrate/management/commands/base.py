import os

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections

from ... import changesets


class BaseChangesetCommand(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label', nargs='*',
            help='App labels of applications to limit the output to.',
        )
        parser.add_argument(
            '--author', action='store', default=os.getlogin(),
            help='Migrations author (defaults to username)',
        )
        parser.add_argument(
            '--fake', action='store_true', default=False,
            help='Create fake changesets (mark migrations ran)',
        )
        parser.add_argument(
            '--skip-errors', action='store_true', default=False,
            help='Skip SQL creation erros',
        )
        parser.add_argument(
            '--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Nominates a database to synchronize. '
                 'Defaults to the "default" database.',
        )
        parser.add_argument(
            '--indent', action='store', default='    ',
            help='Indentation characters (defaults to four spaces)',
        )

    def handle(self, *args, **options):
        db = options['database']
        connection = connections[db]
        app_names = options.pop('app_label')

        try:
            self.handle_changeset_command(connection, app_names, **options)
        except changesets.NoMigrationsFound as ex:
            raise CommandError(ex)
