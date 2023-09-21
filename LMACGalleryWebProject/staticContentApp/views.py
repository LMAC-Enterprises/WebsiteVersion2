import mistletoe
from django.shortcuts import render
from django.http import HttpRequest, HttpResponseNotFound

from LMACGalleryWebProject.core.generalSiteTools import pageTitleHelper, mainMenuHelper
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
            'errorMessage': '',
            'title': pageTitleHelper(content.title)
        },
        'content': {
            'title': content.title,
            'bodyRendered': mistletoe.markdown(content.body),
            'created': content.created_date,
            'contentId': content.content_id,
            'disableTitle': content.disableTitle
        }
    })
