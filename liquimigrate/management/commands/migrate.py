try:
    from django.core.management.commands.migrate import Command as MigrateCommand
except ImportError:
    from django.core.management.base import BaseCommand, CommandError
    MigrateCommand = None


if MigrateCommand:
    class Command(MigrateCommand):
        """
        A custom migrate command that asks you for confirmation
        before migrating the database using standard mechanism.
        """

        def handle(self, *args, **options):
            if options.get("interactive"):
                confirm = raw_input("""
You have requested a database migration using standard Django 1.7+ mechanism.
This CONFLICTS WITH LIQUIMIGRATE.
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """)
            else:
                confirm = "yes"

            if confirm == "yes":
                super(Command, self).handle(**options)
            else:
                print "Migrate cancelled."
else:
    class Command(BaseCommand):
        def handle(self, *args, **kwargs):
            raise CommandError('This command requires Django 1.7+')
