"""
Models.
By quantumg.
"""

import random
import re
from typing import Optional

from django.core.cache import cache
from django.db import models, DatabaseError, transaction, IntegrityError

# https://stackoverflow.com/questions/2248743/django-mysql-full-text-search
from django.db.models import OuterRef, Avg, Q, Count, Subquery
from django.core.exceptions import ObjectDoesNotExist


class Search(models.Lookup):
    """
    TODO: Needs description!
    """
    lookup_name = 'search'

    def as_mysql(self, compiler, connection):
        """
        As_mysql.
        
        :param compiler: Compiler.
        :param connection: Connection.

        :return: No return.
        """
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'MATCH (%s) AGAINST (%s IN BOOLEAN MODE)' % (lhs, rhs), params


models.CharField.register_lookup(Search)
models.TextField.register_lookup(Search)


class LILRatingsModel(models.Model):
    """
    TODO: Needs description!
    """
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
        """
        Rate image.
        
        :param imageId: (int) Image id.
        :param ratingRate: (int) Rating rate.
        :param user: User.

        :return: bool.
        """

        if not user.is_authenticated:
            return False

        defaults = {'score': ratingRate}
        try:
            obj = LILRatingsModel.objects.get(imageid=imageId, uid=user.id)
            for key, value in defaults.items():
                setattr(obj, key, value)
            obj.save()
            return True
        except ObjectDoesNotExist:
            new_values = {'imageid': imageId, 'score': ratingRate, 'uid': user.id}
            new_values.update(defaults)
            obj = LILRatingsModel(**new_values)
            obj.save()
            return True


# Create your models here.
class LILImagesModel(models.Model):
    """
    TODO: Needs description!
    """
    class Meta:
        db_table = 'images'
        managed = False
        verbose_name = 'LIL Image'

    RANDOM_PICK_SIZE = 20

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
        """
        Sanitize search term string.
        
        :param searchTerms: Search terms.

        :return: No return.
        """
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
        """
        Parse search terms.
        
        :param searchTerms: (str) Search terms.
        :param limit: (int) Limit.

        :return: Returns a list.
        """
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
        """
        Make s i d.
        
        :param inputStr: (any) Input str.
        :param defaultSID: (str = '') Default s i d.

        :return: Returns a string.
        """

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
        """
        _paginate result.
        
        :param result: Result.
        :param page: Page.

        :return: No return.
        """
        pageOffset = (page - 1) * LILImagesModel.MAX_IMAGES_PER_PAGE
        if pageOffset > len(result):
            return []
        return result[pageOffset:pageOffset + LILImagesModel.MAX_IMAGES_PER_PAGE]


    @staticmethod
    def loadImages(searchTerms: str, page: int, andMode: bool = True):
        """
        Load images.
        
        :param searchTerms: (str) Search terms.
        :param page: (int) Page.
        :param andMode: (bool = True) And mode.

        :return: No return.
        """
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

        if len(parsedSearchTerms) > 0:
            images = LILImagesModel.objects.raw(
                query,
                [
                    ' '.join(f'+{w}' for w in parsedSearchTerms),
                    LILImagesModel.sanitizeSearchTermString(searchTerms)
                ]
            )
        else:
            images = LILImagesModel.objects.raw(
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

        cache.set(sid, imageList, 3600)

        return LILImagesModel._paginateResult(imageList, page), amountOfImage

    @staticmethod
    def loadImageById(imageId: int):
        """
        Load image by id.
        
        :param imageId: (int) Image id.

        :return: No return.
        """
        try:
            image = LILImagesModel.objects.filter(imageid=imageId).get()
        except ObjectDoesNotExist as e:
            return None

        image.tags = LILImagesModel.parseSearchTerms(image.tags, 25)

        return image

    @staticmethod
    def saveImages(images: list) -> bool:
        """
        Save images.
        
        :param images: (list) Images.

        :return: bool.
        """
        for image in images:
            try:
                obj = LILImagesModel.objects.get(url=image['url'])
            except ObjectDoesNotExist:
                obj = LILImagesModel(
                    title=image['title'],
                    tags=image['tags'],
                    url=image['url'],
                    author=image['author'],
                    permlink=image['permlink']
                )
                obj.save()

        return True

    @staticmethod
    def countImages() -> int:
        """
        Count images.
        

        :return: Returns an integer.
        """
        return LILImagesModel.objects.count()

    @classmethod
    def loadLastHundred(cls, page: int):
        """
        Load last hundred.
        
        :param page: (int) Page.

        :return: No return.
        """
        data = cache.get('lil_last_hundred')

        if data is None:
            ids = list(LILImagesModel.objects.values_list('imageid', flat=True).order_by('-imageid')[:100])
            ratingsSubQuery = LILRatingsModel.objects.filter(imageid=OuterRef('pk')).values('score')
            images = LILImagesModel.objects.filter(pk__in=ids).annotate(ratingscore=Avg(Subquery(ratingsSubQuery))).order_by('-ratingscore')

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

            cache.set('lil_last_hundred', imageList, 3600)
        else:
            imageList = data

        return imageList, len(imageList)

    @staticmethod
    def loadRandomPick():
        """
        Load random pick.
        

        :return: No return.
        """
        data = cache.get('lil_random_pick')

        if data is None:
            ids = list(LILImagesModel.objects.values_list('imageid', flat=True))
            ids = random.choices(ids, k=LILImagesModel.RANDOM_PICK_SIZE)
            ratingsSubQuery = LILRatingsModel.objects.filter(imageid=OuterRef('pk')).values('score')
            images = LILImagesModel.objects.filter(pk__in=ids).annotate(ratingscore=Avg(Subquery(ratingsSubQuery))).order_by('-ratingscore')

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

            cache.set('lil_random_pick', imageList, 15)
        else:
            imageList = data

        return imageList, len(imageList)

    @staticmethod
    def deleteImagesByUrl(images: list) -> Optional[list]:
        """
        Delete images by url.
        
        :param images: (list) Images.

        :return: Optional of "list".
        """
        deleted = []

        for image in images:
            try:
                LILImagesModel.objects.filter(url=image).delete()
                deleted.append(image)
            except DatabaseError:
                continue

        return deleted


class LILTagsModel(models.Model):
    """
    TODO: Needs description!
    """
    class Meta:
        db_table = 'LMACGalleryTags'
        managed = False

    tagText = models.CharField(max_length=512, primary_key=True)
    hits = models.IntegerField()

    @staticmethod
    def makeWeightedTagList(tags: list) -> list:
        """
        Make weighted tag list.
        
        :param tags: (list) Tags.

        :return: Returns a list.
        """
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
        """
        Load all tags.
        
        :param limit: (int = 1000) Limit.

        :return: Returns a list.
        """

        cached = cache.get('lil_gallery_tags_all')
        if cached is not None:
            return cached

        tags = LILTagsModel.objects.all().order_by('-hits')[:limit]
        weightedTags = LILTagsModel.makeWeightedTagList(tags)

        cache.set('lil_gallery_tags_all', weightedTags, 86400)

        return weightedTags

    @staticmethod
    def loadTopTags(limit: int = 100) -> list:
        """
        Load top tags.
        
        :param limit: (int = 100) Limit.

        :return: Returns a list.
        """

        cached = cache.get('lil_gallery_tags')
        if cached is not None:
            return cached

        tags = LILTagsModel.objects.all().order_by('-hits')[:limit]
        weightedTags = LILTagsModel.makeWeightedTagList(tags)

        random.shuffle(weightedTags)

        cache.set('lil_gallery_tags', weightedTags, 86400)

        return weightedTags

    @staticmethod
    def reindexTags():
        """
        Reindex tags.
        

        :return: No return.
        """

        LILTagsModel.objects.all().delete()

        splitRegex = re.compile(r'\w+')
        tags = {}
        readImages = 0
        for imageObject in LILImagesModel.objects.iterator(chunk_size=1000):
            readImages += 1
            for tag in splitRegex.findall(imageObject.tags.lower()):
                if len(tag) < 3:
                    continue

                if len(tag) > 48:
                    continue

                if tag in tags.keys():
                    tags[tag] += 1
                else:
                    tags[tag] = 1
        try:
            with transaction.atomic():
                for tag, hits in tags.items():
                    tagObj = LILTagsModel(tagText=tag, hits=hits)
                    tagObj.save()
        except IntegrityError:
            return False

        return True

