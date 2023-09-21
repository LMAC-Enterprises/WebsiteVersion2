from django.core.management.base import BaseCommand, CommandError

from lilGallery.models import LILTagsModel


class Command(BaseCommand):
    help = "Run it to reindex the LIL tags. This task is a batch"

    def handle(self, *args, **options):
        print(LILTagsModel.reindexTags())
