from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Initialize database with migrations'

    def handle(self, *args, **options):
        try:
            call_command('migrate', verbosity=1)
            self.stdout.write(self.style.SUCCESS('Database initialized successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
