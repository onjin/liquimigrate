from __future__ import absolute_import

from xml.dom import minidom
from xml.parsers.expat import ExpatError

from .base import BaseChangesetCommand, CommandError
from ... import changesets


class Command(BaseChangesetCommand):
    help = "Creates Liquibase changesets for each unapplied Django migration"

    def handle_changeset_command(self, connection, app_names, **options):
        target = changesets.find_target_migration_file(
                                    database=options['database'])
        migration_str = changesets.generate_changesets_text(
                connection, app_names, fake=options['fake'],
                skip_errors=options['skip_errors'], author=options['author'],
                indent=options['indent'])

        if migration_str:
            try:
                doc = minidom.parse(target)
            except ExpatError as ex:
                raise CommandError(
                        'Incorrect syntax of target XML file: %s' % ex)

            nodes = doc.getElementsByTagName('databaseChangeLog')
            if not nodes:
                raise CommandError(
                        'File %s is missing databaseChangeLog' % target)

            with open(target, 'r') as fh:
                original = fh.read()

            updated = original.replace(
                            '</databaseChangeLog>',
                            '%s\n</databaseChangeLog>' % migration_str)

            with open(target, 'w') as fh:
                fh.write(updated)

            print("A new changesets were added to file %s" % target)
        else:
            print("No changesets were added.")
