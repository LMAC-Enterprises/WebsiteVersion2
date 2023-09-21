from django.core.management.base import BaseCommand, CommandError

from lmacAPI.models import LMACAPIAccessModel


class Command(BaseCommand):
    help = "Run it to reset all API Access contingents at once."

    def handle(self, *args, **options):
        LMACAPIAccessModel.resetContingents()
