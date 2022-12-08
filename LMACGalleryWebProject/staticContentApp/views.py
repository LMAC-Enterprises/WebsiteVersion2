import pycmarkgfm
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseNotFound

from LMACGalleryWebProject.core.MainMenu import mainMenuHelper
from staticContentApp.models import StaticContentModel


# Create your views here.
def staticContentAppViewRouter(request: HttpRequest, contentId: str = 'home'):

    if contentId == 'home':
        content = StaticContentModel.getHomePage()
        if content is None:
            return HttpResponseNotFound("Home page not found.")
    else:
        content = StaticContentModel.getPage(contentId)
        if content is None:
            return HttpResponseNotFound("Page not found.")

    return render(request, 'staticContent.html', {
        'overall': {
            'mainMenu': mainMenuHelper(contentId),
            'errorMessage': ''
        },
        'content': {
            'title': content.title,
            'bodyRendered': pycmarkgfm.gfm_to_html(content.body),
            'created': content.created_date,
            'contentId': content.content_id
        }
    })

