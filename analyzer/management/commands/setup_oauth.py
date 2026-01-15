from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Setup Google OAuth'

    def handle(self, *args, **options):
        site = Site.objects.get(pk=1)
        site.domain = 'localhost:8000'
        site.name = 'Text Analysis Services'
        site.save()
        
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth',
                'client_id': 'demo-client-id',
                'secret': 'demo-client-secret',
            }
        )
        google_app.sites.add(site)
        
        self.stdout.write(self.style.SUCCESS('Google OAuth setup complete!'))