try:
    from django.core.management.commands.squashmigrations import Command as MigrateCommand
except ImportError:
    from django.core.management.base import BaseCommand, CommandError
    MigrateCommand = None


if MigrateCommand:
    class Command(MigrateCommand):
        """
        A custom squashmigrations command that asks you for confirmation
        before squashing migrations using standard mechanism.
        """

        def handle(self, *args, **options):
            if options.get("interactive"):
                confirm = raw_input("""
You have requested to squash migrations using standard Django 1.7+ mechanism.
This CONFLICTS WITH LIQUIMIGRATE.
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """)
            else:
                confirm = "yes"

            if confirm == "yes":
                super(Command, self).handle(**options)
            else:
                print "Squashing migrations cancelled."
else:
    class Command(BaseCommand):
        def handle(self, *args, **kwargs):
            raise CommandError('This command requires Django 1.7+')
