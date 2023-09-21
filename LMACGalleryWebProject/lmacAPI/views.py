"""
Views.
By quantumg.
"""

import json
import logging
from abc import ABC, abstractmethod

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from LMACGalleryWebProject.settings import LMAC_API_KEYS
from lilGallery.models import LILImagesModel, LILTagsModel
from lmacAPI.models import LMACAPIAccessModel
from lmacWinners.models import LMACWinnersModel


class LMACAPIV1ViewBase(ABC):
    """
    L m a c a p i v1 view base.
    Derived from ABC.
    """
    API_MODULE = ''
    API_VERSION = ''

    _apiFunctions = {}

    @staticmethod
    def hasFunctionalAccess(apiKey: str, apiModule: str, apiFunction: str) -> bool:
        """
        Has functional access.
        
        :param apiKey: (str) Api key.
        :param apiModule: (str) Api module.
        :param apiFunction: (str) Api function.

        :return: bool.
        """
        if apiKey not in LMAC_API_KEYS.keys():
            return False

        keyPermissions = LMAC_API_KEYS[apiKey]
        print(apiModule)
        print(apiFunction)
        print(apiKey)
        if apiModule not in keyPermissions.keys():
            return False

        if apiFunction not in keyPermissions[apiModule]:
            return False

        return True

    def _checkMandatoryFields(self, requestData: any) -> bool:
        """
        _check mandatory fields.
        
        :param requestData: (any) Request data.

        :return: bool.
        """
        if not isinstance(requestData, dict):
            return False
        if 'apiKey' not in requestData:
            return False
        if 'apiFunction' not in requestData:
            return False
        if 'arguments' not in requestData:
            return False

        return True

    def _createResponse(self, httpStatusCode: int, result: any, error: str = ''):
        """
        _create response.
        
        :param httpStatusCode: (int) Http status code.
        :param result: (any) Result.
        :param error: (str = '') Error.

        :return: No return.
        """
        return JsonResponse(
            {
                'apiVersion': self.__class__.API_VERSION,
                'module': self.__class__.API_MODULE,
                'result': 'error' if len(error) > 0 else result,
                'error': error
            },
            safe=False,
            status=httpStatusCode
        )

    def index(self, request):
        """
        Index.
        
        :param request: Request.

        :return: No return.
        """
        return JsonResponse(
            {
                'apiVersion': self.__class__.API_VERSION,
                'module': self.__class__.API_MODULE,
                'result': 'error',
                'error': 'Method not allowed.'
            },
            safe=False,
            status=405
        )

    def get(self, request):
        """
        Get.
        
        :param request: Request.

        :return: No return.
        """
        return JsonResponse(
            {
                'apiVersion': self.__class__.API_VERSION,
                'module': self.__class__.API_MODULE,
                'result': 'error',
                'error': 'Method not allowed.'
            },
            safe=False,
            status=405
        )

    @staticmethod
    @abstractmethod
    def hasAccess(apiKey: str, apiFunction) -> bool:
        """
        Has access.
        
        :param apiKey: (str) Api key.
        :param apiFunction: Api function.

        :return: bool.
        """
        pass

    def post(self, request):
        """
        Post.
        
        :param request: Request.

        :return: No return.
        """

        requestData = json.loads(request.body)

        if not self._checkMandatoryFields(requestData):
            return self._createResponse(400, 'error', 'Bad request.')

        if requestData['apiKey'] not in LMAC_API_KEYS.keys():
            return self._createResponse(401, 'error', 'Unauthorized.')

        if not LMACAPIAccessModel.openContingent(requestData['apiKey']):
            return self._createResponse(412, 'error', 'Contingent completely consumed.')

        if requestData['apiFunction'] not in self._apiFunctions.keys():
            return self._createResponse(404, 'error', 'API function not Found.')

        if not self.__class__.hasAccess(
                requestData['apiKey'],
                requestData['apiFunction']
        ):
            return self._createResponse(403, 'error', 'Forbidden.')

        try:
            return self._apiFunctions[requestData['apiFunction']](requestData['arguments'])
        except Exception as e:
            logging.Logger.error('Internal error while serving API request: ' + str(e), exc_info=e)
            return self._createResponse(500, 'error', 'Internal error.')


@method_decorator(csrf_exempt, name='dispatch')
class LMACApiV1LILView(View, LMACAPIV1ViewBase):
    """
    L m a c api v1 l i l view.
    Derived from View, LMACAPIV1ViewBase.
    """
    API_MODULE = 'lil'
    API_VERSION = 'v1'

    def __init__(self, **kwargs):
        """
        Constructor.
        
        :param **kwargs: **kwargs.

        :return: No return.
        """
        super().__init__(**kwargs)

        self._apiFunctions = {
            'addBunch': self._apiFunction_addBunch,
            'count': self._apiFunction_count,
            'randomPick': self._apiFunction_randomPick,
            'deleteBunch': self._apiFunction_deleteBunch,
            'getTags': self._apiFunction_getTags,
            'getTopTags': self._apiFunction_getTopTags,
        }

    @staticmethod
    def hasAccess(apiKey: str, apiFunction) -> bool:
        """
        Has access.
        
        :param apiKey: (str) Api key.
        :param apiFunction: Api function.

        :return: bool.
        """
        return LMACApiV1LILView.hasFunctionalAccess(
            apiKey,
            LMACApiV1LILView.API_MODULE,
            apiFunction
        )

    def _apiFunction_addBunch(self, arguments: dict):
        """
        _api function_add bunch.
        
        :param arguments: (dict) Arguments.

        :return: No return.
        """

        if 'images' not in arguments.keys():
            return self._createResponse(400, 'error', 'Missing images field.')
        if not isinstance(arguments['images'], list):
            return self._createResponse(400, 'error', 'Images field malformed.')

        images = arguments['images']
        if len(images) > 100:
            return self._createResponse(413, 'error', 'Too many images per request.')

        if not LILImagesModel.saveImages(images):
            return self._createResponse(501, 'error', 'Internal error. Call the admin.')

        return self._createResponse(200, 'ok')

    def _apiFunction_count(self, arguments: dict):
        """
        _api function_count.
        
        :param arguments: (dict) Arguments.

        :return: No return.
        """
        return self._createResponse(200, LILImagesModel.countImages())

    def _apiFunction_randomPick(self, arguments: dict):
        """
        _api function_random pick.
        
        :param arguments: (dict) Arguments.

        :return: No return.
        """
        pick, amount = LILImagesModel.loadRandomPick()

        for picked in pick:
            del picked['ratingScore']

        return self._createResponse(200, pick)

    def _apiFunction_deleteBunch(self, arguments: dict):
        """
        _api function_delete bunch.
        
        :param arguments: (dict) Arguments.

        :return: No return.
        """

        if 'images' not in arguments.keys():
            return self._createResponse(400, 'error', 'Missing images field.')
        if not isinstance(arguments['images'], list):
            return self._createResponse(400, 'error', 'Images field malformed.')

        images = arguments['images']
        if len(images) > 100:
            return self._createResponse(413, 'error', 'Too many images per request.')

        imagesDeleted = LILImagesModel.deleteImagesByUrl(images)
        if imagesDeleted is None:
            return self._createResponse(501, 'error', 'Internal error. Call the admin.')

        return self._createResponse(
            200, {
                'succeeded': True,
                'deleted': imagesDeleted
            }
        )

    def _apiFunction_getTags(self, arguments: dict):
        """
        _api function_get tags.
        
        :param arguments: (dict) Arguments.

        :return: No return.
        """
        return self._createResponse(200, LILTagsModel.loadAllTags())

    def _apiFunction_getTopTags(self, arguments: dict):
        """
        _api function_get top tags.
        
        :param arguments: (dict) Arguments.

        :return: No return.
        """
        return self._createResponse(200, LILTagsModel.loadTopTags())


@method_decorator(csrf_exempt, name='dispatch')
class LMACApiV1LMACView(View, LMACAPIV1ViewBase):
    """
    L m a c api v1 l m a c view.
    Derived from View, LMACAPIV1ViewBase.
    """
    API_MODULE = 'lmac'
    API_VERSION = 'v1'

    def __init__(self, **kwargs):
        """
        Constructor.
        
        :param **kwargs: **kwargs.

        :return: No return.
        """
        super().__init__(**kwargs)

        self._apiFunctions = {
            'addContestOutcomes': self._apiFunction_addContestOutcomes,
            'getLastContestWinners': self._apiFunction_getLastContestWinners
        }

    @staticmethod
    def hasAccess(apiKey: str, apiFunction) -> bool:
        """
        Has access.
        
        :param apiKey: (str) Api key.
        :param apiFunction: Api function.

        :return: bool.
        """

        return LMACApiV1LMACView.hasFunctionalAccess(
            apiKey,
            LMACApiV1LMACView.API_MODULE,
            apiFunction
        )

    def _apiFunction_addContestOutcomes(self, arguments: dict):
        """
        _api function_add contest outcomes.
        
        :param arguments: (dict) Arguments.

        :return: No return.
        """

        if 'outcomes' not in arguments.keys():
            return self._createResponse(400, 'error', 'Missing outcomes field.')
        if not isinstance(arguments['outcomes'], list):
            return self._createResponse(400, 'error', 'Outcomes field malformed.')

        LMACWinnersModel.addContestOutcomes(arguments['outcomes'])

        return self._createResponse(200, 'ok')

    def _apiFunction_getLastContestWinners(self, arguments: dict):
        """
        _api function_get last contest winners.
        
        :param arguments: (dict) Arguments.

        :return: No return.
        """

        winners = LMACWinnersModel.getLastContestWinnerCollages()

        return self._createResponse(200, winners)
