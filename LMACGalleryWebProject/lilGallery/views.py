"""
Views.
By quantumg.
"""

import json

from django.contrib import auth
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render

# Create your views here.
from LMACGalleryWebProject.core.generalSiteTools import pageTitleHelper, mainMenuHelper
from lilGallery.models import LILImagesModel, LILRatingsModel, LILTagsModel


def lilGalleryMainAppView(request: HttpRequest, searchTerms: str = '', page: int = 1):
    """
    Lil gallery main app view.
    
    :param request: (HttpRequest) Request.
    :param searchTerms: (str = '') Search terms.
    :param page: (int = 1) Page.

    :return: No return.
    """
    if page < 1:
        page = 1

    andMode = True
    if 'mode' in request.GET.keys() and request.GET.get('mode', ''):
        andMode = False

    errorMessage = ''

    sanitizedSearchTerms = searchTerms.strip().lower();

    if sanitizedSearchTerms == 'random-pick':
        images, amountOfImages = LILImagesModel.loadRandomPick()
    elif sanitizedSearchTerms == 'last-hundred':
        images, amountOfImages = LILImagesModel.loadLastHundred(page)
    else:
        images, amountOfImages = LILImagesModel.loadImages(searchTerms, page, andMode)
        if len(images) == 0:
            errorMessage = 'Sorry, couldn\'t find any images matching your search query.'

    return render(request, 'lilGalleryMain.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lil-gallery'),
            'errorMessage': errorMessage,
            'title': pageTitleHelper('LIL')
        },
        'searchTerms': ' '.join(LILImagesModel.parseSearchTerms(searchTerms, 5)),
        'content': {
            'page': page,
            'pagesAvailable': 1,
            'images': images,
            'imagesTotal': amountOfImages
        }
    })


def lilGalleryAjaxAppView(request: HttpRequest):
    """
    Lil gallery ajax app view.
    
    :param request: (HttpRequest) Request.

    :return: No return.
    """
    if request.method != 'POST':
        return HttpResponse(status=405, content='Error. Forbidden request.')

    page = int(request.POST['data[page]'])
    searchTerms = request.POST['data[searchTerms]']
    if searchTerms.startswith('@'):
        searchTerms = searchTerms[1:]

    if page < 1:
        page = 1

    andMode = True
    if 'mode' in request.GET.keys() and request.GET.get('mode', ''):
        andMode = False

    images, amountOfImages = LILImagesModel.loadImages(searchTerms, page, andMode)
    if len(images) == 0:
        return HttpResponse(status=404, content='Sorry, couldn\'t find any more images matching your search query.')

    response = render(request, 'lilGalleryAjax.html', {
        'content': {
            'page': page,
            'pagesAvailable': 1,
            'images': images,
            'searchTerms': '',
            'imagesTotal': amountOfImages
        }
    })
    response['lil-images-amount'] = amountOfImages
    return response


def lilGalleryImageMainAppView(request: HttpRequest, imageId: int = 0):
    """
    Lil gallery image main app view.
    
    :param request: (HttpRequest) Request.
    :param imageId: (int = 0) Image id.

    :return: No return.
    """
    image = LILImagesModel.loadImageById(imageId)
    if image is None:
        return HttpResponseNotFound("Not found.")

    return render(
        request,
        'lilGalleryImageMain.html',
        {
            'overall': {
                'mainMenu': mainMenuHelper('lil-gallery'),
                'errorMessage': '',
                'title': pageTitleHelper('Image')
            },
            'image': image
        }
    )


def lilGalleryImageAjaxAppView(request: HttpRequest):
    """
    Lil gallery image ajax app view.
    
    :param request: (HttpRequest) Request.

    :return: No return.
    """
    if request.method != 'POST':
        return HttpResponse(status=405, content='Error. Forbidden request.')

    imageId = int(request.POST['data[imageId]'])

    image = LILImagesModel.loadImageById(imageId)
    if image is None:
        return HttpResponseNotFound("hello")

    return render(
        request,
        'lilGalleryImageAjax.html',
        {
            'image': image
        }
    )


def _lilGalleryAjaxCommand_doFiveStarVote(arguments: dict, user) -> dict:
    """
    _lil gallery ajax command_do five star vote.
    
    :param arguments: (dict) Arguments.
    :param user: User.

    :return: Returns a dict.
    """
    print(user)

    if not user.has_perm("blog.rate_image"):
        return {
            'success': False,
            'errorMessage': 'Not allowed.'
        }

    if not LILRatingsModel.rateImage(
            arguments['parameters']['imageId'],
            arguments['parameters']['ratingRate'],
            user
    ):
        return {
            'success': False,
            'errorMessage': 'Failed rating the image.'
        }

    return {
        'success': True,
        'command': arguments['command'],
        'imageId': arguments['parameters']['imageId'],
        'ratingRate': arguments['parameters']['ratingRate']
    }


def lilGalleryAjaxCommand(request: HttpRequest):
    """
    Lil gallery ajax command.
    
    :param request: (HttpRequest) Request.

    :return: No return.
    """
    if not request.method == "POST":
        return JsonResponse(
            {
                'success': False,
                'errorMessage': 'Method not allowed.'
            }
        )

    commandData = json.loads(request.POST.get('data'))
    commands = {
        'doFiveStarVote': _lilGalleryAjaxCommand_doFiveStarVote
    }
    print(commandData)
    if commandData['command'] not in commands.keys():
        return JsonResponse(
            {
                'success': False,
                'errorMessage': 'Command not available.'
            }
        )

    return JsonResponse(
        commands[commandData['command']](commandData, request.user)
    )


def lilGalleryTagsView(request: HttpRequest, allTags=False):
    """
    Lil gallery tags view.
    
    :param request: (HttpRequest) Request.
    :param allTags=False: All tags= false.

    :return: No return.
    """

    return render(request, 'lilGalleryTags.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lil-gallery-tags'),
            'errorMessage': '',
            'title': pageTitleHelper('Tags')
        },
        'topTags': LILTagsModel.loadTopTags(),
        'allTags': LILTagsModel.loadAllTags()
    })


def lilGalleryAllTagsView(request: HttpRequest):
    """
    Lil gallery all tags view.
    
    :param request: (HttpRequest) Request.

    :return: No return.
    """
    return lilGalleryTagsView(request, True)

