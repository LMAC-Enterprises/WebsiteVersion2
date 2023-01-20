import random
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
        permissions = [
            (
                "rate_image",
                "Allowed to rate an image."
            )
        ]

    ratingid = models.IntegerField(primary_key=True)
    imageid = models.IntegerField()
    score = models.IntegerField()
    uid = models.IntegerField()

    @staticmethod
    def rateImage(imageId: int, ratingRate: int, user) -> bool:

        if not user.is_authenticated:
            return False

        defaults = {'score': ratingRate}
        try:
            obj = LILRatingsModel.objects.using(LILImagesModel.DJANGO_DATABASE_ID).get(imageid=imageId, uid=user.id)
            for key, value in defaults.items():
                setattr(obj, key, value)
            obj.save()
            return True
        except LILRatingsModel.DoesNotExist:
            new_values = {'imageid': imageId, 'score': ratingRate, 'uid': user.id}
            new_values.update(defaults)
            obj = LILRatingsModel(**new_values)
            obj.save(using=LILImagesModel.DJANGO_DATABASE_ID)
            return True


# Create your models here.
class LILImagesModel(models.Model):
    class Meta:
        db_table = 'images'
        managed = False
        verbose_name = 'LIL Image'

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
            r'/[^A-Za-z0-9_\-\.]/',
            '',
            searchTerms
        )

    @staticmethod
    def parseSearchTerms(searchTerms: str, limit: int) -> list:
        parsedSearchTerms = []
        parsedSearchTermBuffer = ''
        stoppers = ['\n', '\t', ' ', ',', '\r']
        additionalAllowed = ['.', '-']

        for character in searchTerms:
            if character.isalnum() or character in additionalAllowed:
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
            return 'lil_' + LILImagesModel.sanitizeSearchTermString(inputStr)

    @staticmethod
    def _paginateResult(result, page):
        pageOffset = (page - 1) * LILImagesModel.MAX_IMAGES_PER_PAGE
        if pageOffset > len(result):
            return []
        return result[pageOffset:pageOffset + LILImagesModel.MAX_IMAGES_PER_PAGE]


    @staticmethod
    def loadImages(searchTerms: str, page: int, andMode: bool = True):
        parsedSearchTerms = LILImagesModel.parseSearchTerms(searchTerms, LILImagesModel.MAX_SEARCH_TERMS_PER_QUERY)
        sid = LILImagesModel.makeSID(parsedSearchTerms, 'empty') + ('_AND' if andMode else '_OR')

        cached = cache.get(sid)
        if cached is not None:
            return LILImagesModel._paginateResult(cached, page), len(cached)

        if len(parsedSearchTerms) == 0 or parsedSearchTerms[0] == 'all':
            parsedSearchTerms = []

        andModeExpression = ''
        if andMode:
            andModeExpression = ' IN BOOLEAN MODE'

        query = 'SELECT imageid, title, tags, url, permlink, author, (SELECT AVG(score) FROM lmacg_ratings as lr ' \
                'WHERE lr.imageid=li.imageid) AS ratingscore FROM images AS li '
        if len(parsedSearchTerms) > 0:
            query += 'WHERE MATCH(li.tags) AGAINST(%s' + andModeExpression + ') OR li.author=%s '
        query += 'ORDER BY ratingscore DESC'
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
                    LILImagesModel.sanitizeSearchTermString(searchTerms)
                ]
            )
        else:
            images = LILImagesModel.objects.using(LILImagesModel.DJANGO_DATABASE_ID).raw(
                query
            )

        amountOfImage = len(images)

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

        del images

        cache.set(sid, imageList)

        return LILImagesModel._paginateResult(imageList, page), amountOfImage

    @staticmethod
    def loadImageById(imageId: int):
        try:
            image = LILImagesModel.objects.using(LILImagesModel.DJANGO_DATABASE_ID).filter(imageid=imageId).get()
        except ObjectDoesNotExist as e:
            return None

        image.tags = LILImagesModel.parseSearchTerms(image.tags, 25)

        return image


class LILTagsModel(models.Model):
    class Meta:
        db_table = 'LMACGalleryTags'
        managed = False

    DJANGO_DATABASE_ID = 'lmacMysql'

    tagText = models.CharField(max_length=512, primary_key=True)
    hits = models.IntegerField()

    @staticmethod
    def makeWeightedTagList(tags: list) -> list:
        weightedTags = []

        mostHits = 0
        for tag in tags:
            if tag.hits > mostHits:
                mostHits = tag.hits

        for tag in tags:
            tagInfo = {
                'tagText': tag.tagText,
                'hits': tag.hits,
                'weight': int((100.0 / float(mostHits)) * float(tag.hits))
            }
            if tagInfo['weight'] >= 75.0:
                tagInfo['class'] = 'top-1'
            elif tagInfo['weight'] < 75.0 and tagInfo['weight'] > 50.0:
                tagInfo['class'] = 'top-2'
            elif tagInfo['weight'] <= 50.0 and tagInfo['weight'] > 25.0:
                tagInfo['class'] = 'top-3'
            else:
                tagInfo['class'] = 'top-4'

            weightedTags.append(
                tagInfo
            )

        return weightedTags

    @staticmethod
    def loadAllTags(limit: int = 1000) -> list:

        cached = cache.get('lil_gallery_tags_all')
        if cached is not None:
            return cached

        tags = LILTagsModel.objects.using(LILTagsModel.DJANGO_DATABASE_ID).all().order_by('-hits')
        weightedTags = LILTagsModel.makeWeightedTagList(tags)

        cache.set('lil_gallery_tags_all', weightedTags)

        return weightedTags

    @staticmethod
    def loadTopTags(limit: int = 100) -> list:

        cached = cache.get('lil_gallery_tags')
        if cached is not None:
            return cached

        tags = LILTagsModel.objects.using(LILTagsModel.DJANGO_DATABASE_ID).all().order_by('-hits')[:limit]
        weightedTags = LILTagsModel.makeWeightedTagList(tags)

        random.shuffle(weightedTags)

        cache.set('lil_gallery_tags', weightedTags)

        return weightedTags
