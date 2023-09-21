"""
Views.
By quantumg.
"""

from django.http import HttpRequest
from django.shortcuts import render

from LMACGalleryWebProject.core.generalSiteTools import mainMenuHelper, pageTitleHelper


def lilCheckerMainView(request: HttpRequest):
    """
    Lil checker main view.
    
    :param request: (HttpRequest) Request.

    :return: No return.
    """
    return render(request, 'lilCheckerMain.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lil-checker'),
            'errorMessage': '',
            'title': pageTitleHelper('LIL Checker')
        }
    })
