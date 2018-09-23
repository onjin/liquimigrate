from __future__ import absolute_import

from .base import BaseChangesetCommand
from ... import changesets


class Command(BaseChangesetCommand):
    help = "Generates SQL changesets for each unapplied Django migration"

    def handle_changeset_command(self, connection, app_names, **options):
        docstr = changesets.generate_changesets_text(
                connection, app_names, fake=options['fake'],
                skip_errors=options['skip_errors'], author=options['author'],
                indent=options['indent'])
        print(docstr)
