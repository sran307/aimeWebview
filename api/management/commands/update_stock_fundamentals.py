from django.core.management.base import BaseCommand
from api.views import *  # Import your function

class Command(BaseCommand):
    help = 'Update stock fundamentals monthly'

    def handle(self, *args, **kwargs):
        GetFundas(None)
        self.stdout.write(self.style.SUCCESS('Stock fundamentals updated successfully'))
