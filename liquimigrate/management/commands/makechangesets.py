import os

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader


class Command(BaseCommand):
    help = "Generates SQL changesets for each unapplied Django migration"

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
            '--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Nominates a database to synchronize. '
                 'Defaults to the "default" database.',
        )

    def handle(self, *args, **options):
        db = options['database']
        connection = connections[db]
        app_names = options['app_label']
        author = options['author'] or os.getlogin()

        self.generate_changesets(connection, app_names, author)

    def _validate_app_names(self, loader, app_names, author):
        invalid_apps = []
        for app_name in app_names:
            if app_name not in loader.migrated_apps:
                invalid_apps.append(app_name)
        if invalid_apps:
            raise CommandError(
                    'No migrations present for: %s' % (
                        ', '.join(sorted(invalid_apps))))

    def generate_changesets(self, connection, app_names, author):
        loader = MigrationLoader(connection)
        graph = loader.graph
        if app_names:
            self._validate_app_names(loader, app_names)
            targets = [
                    key for key in graph.leaf_nodes()
                    if key[0] in app_names]
        else:
            targets = graph.leaf_nodes()
        plan = []
        seen = set()

        # Generate the plan
        for target in targets:
            for migration in graph.forwards_plan(target):
                if migration not in seen:
                    node = graph.node_map[migration]
                    plan.append(node)
                    seen.add(migration)

        to_generate = []

        for node in plan:
            if node.key not in loader.applied_migrations:
                to_generate.append(node)

        executor = MigrationExecutor(connection)

        for app_label, name in to_generate:
            migration = executor.loader.get_migration_by_prefix(
                                                        app_label, name)
            targets = [(app_label, migration.name)]
            forward_plan = [(executor.loader.graph.nodes[targets[0]], False)]
            backward_plan = [(executor.loader.graph.nodes[targets[0]], True)]

            sql_forward = executor.collect_sql(forward_plan)
            sql_backward = executor.collect_sql(backward_plan)

            forward_version = (
                    'insert into django_migrations (app, name, applied) '
                    'values (\'%s\', \'%s\', now());' % (
                        app_label, migration.name))
            backward_version = (
                    'delete from django_migrations where '
                    'app=\'%s\' and name=\'%s\';' % (
                            app_label, migration.name))

            print('    <changeSet id="django-%s-%s" author="%s">' % (
                app_label, migration.name, author))
            print('        <sql><![CDATA[')
            print('            '+'\n            '.join(sql_forward))
            print('        ]]></sql>')
            print('        <sql>%s</sql>' % forward_version)
            print('        <rollback>')
            print('            <sql><![CDATA[')
            print('            '+'\n            '.join(sql_backward))
            print('            ]]></sql>')
            print('            <sql>%s</sql>' % backward_version)
            print('        </rollback>')
            print('    </changeSet>')
