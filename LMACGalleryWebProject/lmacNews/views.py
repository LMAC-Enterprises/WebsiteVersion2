from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.
from LMACGalleryWebProject.core.generalSiteTools import mainMenuHelper, pageTitleHelper
from lmacNews.models import LMACNewsModel


def lmacNewsIndexView(request: HttpRequest):
    errorMessage = ''

    news = LMACNewsModel.loadNews()
    if news is None:
        errorMessage = 'Can\'t load the news at the moment.'

    return render(request, 'lmacNews.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lmac-news'),
            'errorMessage': errorMessage,
            'title': pageTitleHelper('News')
        },
        'posts': news,
        'postCount': len(news)
    })