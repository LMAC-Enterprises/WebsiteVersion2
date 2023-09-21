"""
Models.
By quantumg.
"""

from typing import Optional

from django.core.cache import cache
from django.db import models

from LMACGalleryWebProject.core.hiveNetwork import HiveAccountPostsRequest


class LMACNewsModel:
    """
    L m a c news model.
    """
    MAX_NEWS = 8
    CACHE_TIME_IN_SECONDS = 3600

    @staticmethod
    def loadNews() -> Optional[list]:
        """
        Load news.
        

        :return: Optional of "list".
        """

        cached = cache.get('lmac_news')
        if cached is not None:
            return cached

        news = HiveAccountPostsRequest('lmac', LMACNewsModel.MAX_NEWS).submit()
        if news is None:
            return []

        cache.set('lmac_news', news,  LMACNewsModel.CACHE_TIME_IN_SECONDS)

        return news

