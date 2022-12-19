import json

from django.contrib import auth
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render

# Create your views here.
from LMACGalleryWebProject.core.MainMenu import mainMenuHelper
from lilGallery.models import LILImagesModel, LILRatingsModel, LILTagsModel


def lilGalleryMainAppView(request: HttpRequest, searchTerms: str = '', page: int = 1):
    if page < 1:
        page = 1

    errorMessage = ''
    images, amountOfImages = LILImagesModel.loadImages(searchTerms, page)
    if len(images) == 0:
        errorMessage = 'Sorry, couldn\'t find any images matching your search query.'

    return render(request, 'lilGalleryMain.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lil-gallery'),
            'errorMessage': errorMessage
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
    if request.method != 'POST':
        return HttpResponse(status=405, content='Error. Forbidden request.')

    page = int(request.POST['data[page]'])
    searchTerms = request.POST['data[searchTerms]']

    if page < 1:
        page = 1

    images, amountOfImages = LILImagesModel.loadImages(searchTerms, page)
    if len(images) == 0:
        return HttpResponse(status=404, content='Sorry, couldn\'t find any images matching your search query.')

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
    image = LILImagesModel.loadImageById(imageId)
    if image is None:
        return HttpResponseNotFound("hello")

    return render(
        request,
        'lilGalleryImageMain.html',
        {
            'overall': {
                'mainMenu': mainMenuHelper('lil-gallery'),
                'errorMessage': ''
            },
            'image': image
        }
    )


def lilGalleryImageAjaxAppView(request: HttpRequest):
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

    return render(request, 'lilGalleryTags.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lil-gallery-tags'),
            'errorMessage': ''
        },
        'topTags': LILTagsModel.loadTopTags(),
        'allTags': LILTagsModel.loadAllTags()
    })


def lilGalleryAllTagsView(request: HttpRequest):
    return lilGalleryTagsView(request, True)

