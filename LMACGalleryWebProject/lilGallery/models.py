import re

from django.core.cache import cache
from django.db import models


# https://stackoverflow.com/questions/2248743/django-mysql-full-text-search
from django.db.models import OuterRef, Avg, Q
from django.core.exceptions import ObjectDoesNotExist


class Search(models.Lookup):
    lookup_name = 'search'

    def as_mysql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'MATCH (%s) AGAINST (%s IN BOOLEAN MODE)' % (lhs, rhs), params


models.CharField.register_lookup(Search)
models.TextField.register_lookup(Search)


class LILRatingsModel(models.Model):
    class Meta:
        db_table = 'lmacg_ratings'
        managed = False

    ratingid = models.IntegerField(primary_key=True)
    imageid = models.ForeignKey(
        'LILImagesModel', default=1, verbose_name="Ratings", on_delete=models.SET_DEFAULT)
    score = models.IntegerField()
    uid = models.IntegerField()


# Create your models here.
class LILImagesModel(models.Model):
    class Meta:
        db_table = 'images'
        managed = False

    DJANGO_DATABASE_ID = 'lmacMysql'

    MAX_IMAGES_PER_PAGE = 20
    MAX_SEARCH_TERM_FRAGMENT_SIZE = 32
    MIN_SEARCH_TERM_FRAGMENT_SIZE = 3
    MAX_SEARCH_TERMS_PER_QUERY = 5

    imageid = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=512)
    tags = models.TextField()
    url = models.CharField(max_length=512)
    permlink = models.CharField(max_length=512)
    author = models.TextField()

    @staticmethod
    def sanitizeSearchTermString(searchTerms):
        searchTermsSize = len(searchTerms)

        if searchTermsSize == 0:
            return ''

        if searchTermsSize > LILImagesModel.MAX_SEARCH_TERM_FRAGMENT_SIZE:
            searchTerms = searchTerms[:LILImagesModel.MAX_SEARCH_TERM_FRAGMENT_SIZE]

        return re.sub(
            r'/[^A-Za-z0-9_\.\-]/',
            '',
            searchTerms
        )

    @staticmethod
    def parseSearchTerms(searchTerms: str, limit: int) -> list:
        parsedSearchTerms = []
        parsedSearchTermBuffer = ''
        stoppers = ['\n', '\t', ' ', '.', ',', '-', '\r']

        for character in searchTerms:
            if character.isalnum():
                parsedSearchTermBuffer += character
            if character in stoppers:
                bufferSize = len(parsedSearchTermBuffer)
                if bufferSize >= 3:
                    if bufferSize > LILImagesModel.MAX_SEARCH_TERM_FRAGMENT_SIZE:
                        parsedSearchTermBuffer = parsedSearchTermBuffer[:LILImagesModel.MAX_SEARCH_TERM_FRAGMENT_SIZE]
                    parsedSearchTerms.append(parsedSearchTermBuffer.lower())
                parsedSearchTermBuffer = ''

            if len(parsedSearchTerms) == limit:
                break

        if len(parsedSearchTermBuffer) >= 3 and len(parsedSearchTerms) < LILImagesModel.MAX_SEARCH_TERMS_PER_QUERY:
            parsedSearchTerms.append(parsedSearchTermBuffer.lower())

        return parsedSearchTerms

    @staticmethod
    def makeSID(inputStr: any, defaultSID: str = '') -> str:

        if isinstance(inputStr, list):
            if len(inputStr) > 0:
                return 'lil_' + ('_'.join(inputStr))
            else:
                return 'lil_' + defaultSID
        elif isinstance(inputStr, str):
            inputStr = '_'.join(LILImagesModel.parseSearchTerms(inputStr, 10))
            if len(inputStr) > 0:
                return 'lil_' + inputStr
            else:
                return 'lil_' + defaultSID
        else:
            inputStr = LILImagesModel.sanitizeSearchTermString(inputStr)

    @staticmethod
    def loadImages(searchTerms: str, page: int):
        parsedSearchTerms = LILImagesModel.parseSearchTerms(searchTerms, LILImagesModel.MAX_SEARCH_TERMS_PER_QUERY)
        sid = LILImagesModel.makeSID(parsedSearchTerms, 'empty')

        cached = cache.get(sid)
        if cached is not None:
            return cached

        if len(parsedSearchTerms) == 0 or parsedSearchTerms[0] == 'all':
            parsedSearchTerms = []

        query = 'SELECT imageid, title, tags, url, permlink, author, (SELECT AVG(score) FROM lmacg_ratings as lr ' \
                'WHERE lr.imageid=li.imageid) AS ratingscore FROM images AS li '
        if len(parsedSearchTerms) > 0:
            query += 'WHERE MATCH(li.tags) AGAINST(%s IN BOOLEAN MODE) OR li.author=%s '
        query += 'ORDER BY ratingscore DESC LIMIT %s, %s'
        """query = query.format(
                author=LILImagesModel.sanitizeSearchTermString(searchTerms),
                searchTerms=' '.join(f'+{w}' for w in parsedSearchTerms),
                pageOffset=(page - 1) * LILImagesModel.MAX_IMAGES_PER_PAGE,
                pageSize=LILImagesModel.MAX_IMAGES_PER_PAGE
        )"""
        if len(parsedSearchTerms) > 0:
            images = LILImagesModel.objects.using(LILImagesModel.DJANGO_DATABASE_ID).raw(
                query,
                [
                    ' '.join(f'+{w}' for w in parsedSearchTerms),
                    LILImagesModel.sanitizeSearchTermString(searchTerms),
                    (page - 1) * LILImagesModel.MAX_IMAGES_PER_PAGE,
                    LILImagesModel.MAX_IMAGES_PER_PAGE
                ]
            )
        else:
            images = LILImagesModel.objects.using(LILImagesModel.DJANGO_DATABASE_ID).raw(
                query,
                [
                    (page - 1) * LILImagesModel.MAX_IMAGES_PER_PAGE,
                    LILImagesModel.MAX_IMAGES_PER_PAGE
                ]
            )

        imageList = []
        for image in images:
            imageList.append(
                {
                    'imageId': image.imageid,
                    'title': image.title,
                    'tags': LILImagesModel.parseSearchTerms(image.tags, 5),
                    'autorperm': '@{author}/{permlink}'.format(author=image.author, permlink=image.permlink),
                    'imageUrl': image.url,
                    'ratingScore': image.ratingscore
                }
            )

        cache.set(sid, imageList)

        return imageList

    @staticmethod
    def loadImageById(imageId: int):
        try:
            image = LILImagesModel.objects.using(LILImagesModel.DJANGO_DATABASE_ID).filter(imageid=imageId).get()
        except ObjectDoesNotExist as e:
            return None

        image.tags = LILImagesModel.parseSearchTerms(image.tags, 25)

        return image


