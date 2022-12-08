from typing import Optional

from django.db import models


# Create your models here.
class StaticContentModel(models.Model):
    content_id = models.CharField(max_length=48)
    is_enabled = models.BooleanField(default=True)
    is_home_page = models.BooleanField(default=False)
    created_date = models.DateField()
    title = models.CharField(max_length=256)
    body = models.TextField()

    @staticmethod
    def getHomePage() -> Optional['StaticContentModel']:

        content = StaticContentModel.objects.filter(is_home_page=True)
        if len(content) == 0:
            return None

        return content[0]

    @staticmethod
    def getPage(contentId):
        content = StaticContentModel.objects.filter(content_id=contentId)
        if len(content) == 0:
            return None

        return content[0]
