from django.core.management import call_command
from django.db import connection
import os

_db_initialized = False

class InitializeDBMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        global _db_initialized
        if not _db_initialized:
            self._init_db()
            _db_initialized = True

    def _init_db(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';")
                if not cursor.fetchone():
                    call_command('migrate', verbosity=0)
        except Exception:
            try:
                call_command('migrate', verbosity=0)
            except Exception:
                pass

    def __call__(self, request):
        return self.get_response(request)
