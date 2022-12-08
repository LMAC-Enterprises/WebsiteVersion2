from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import render


# Create your views here.
from LMACGalleryWebProject.core.MainMenu import mainMenuHelper
from lilGallery.models import LILImagesModel


def lilGalleryMainAppView(request: HttpRequest, searchTerms: str = '', page: int = 1):

    if page < 1:
        page = 1

    errorMessage = ''
    images = LILImagesModel.loadImages(searchTerms, page)
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
        }
    })


def lilGalleryAjaxAppView(request: HttpRequest):

    if request.method != 'POST':
        return HttpResponse(status=405, content='Error. Forbidden request.')

    page = int(request.POST['data[page]'])
    searchTerms = request.POST['data[searchTerms]']

    if page < 1:
        page = 1

    images = LILImagesModel.loadImages(searchTerms, page)
    if len(images) == 0:
        return HttpResponse(status=404, content='Sorry, couldn\'t find any images matching your search query.')

    return render(request, 'lilGalleryAjax.html', {
        'content': {
            'page': page,
            'pagesAvailable': 1,
            'images': images,
            'searchTerms': ''
        }
    })


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
