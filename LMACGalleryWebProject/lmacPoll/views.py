"""
Views.
By quantumg.
"""

import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.

from LMACGalleryWebProject.core.generalSiteTools import pageTitleHelper, mainMenuHelper
from lmacPoll.models import LMACPollModel, LMACPollPostTemplateModel


def lmacPollMainAppView(request: HttpRequest):
    """
    Lmac poll main app view.
    
    :param request: (HttpRequest) Request.

    :return: No return.
    """

    errorMessage = ''
    polls = LMACPollModel.loadPolls()
    if not polls:
        errorMessage = 'Internal error. Please contact the admin.'

    return render(request, 'lmacPollsMain.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lmac-polls'),
            'errorMessage': errorMessage,
            'title': pageTitleHelper('Polls')
        },
        'polls': polls
    })


def lmacPollView(request: HttpRequest, author: str = '', permlink: str = ''):
    """
    Lmac poll view.
    
    :param request: (HttpRequest) Request.
    :param author: (str = '') Author.
    :param permlink: (str = '') Permlink.

    :return: No return.
    """

    if len(author) == 0 or len(permlink) == 0:
        return HttpResponse(status=404, content='Sorry, couldn\'t find poll post.')

    errorMessage = ''
    poll = LMACPollModel.loadPoll('@%s/%s' % (author, permlink))
    if not poll:
        errorMessage = 'Failed loading poll post.'

    return render(request, 'lmacPoll.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lmac-polls'),
            'errorMessage': errorMessage,
            'title': pageTitleHelper('Poll')
        },
        'poll': poll
    })


def lmacPollCreatePollView(request: HttpRequest):
    """
    Lmac poll create poll view.
    
    :param request: (HttpRequest) Request.

    :return: No return.
    """
    if request.method == 'GET':
        selectedPollTemplateName = request.GET.get('template', 'Default template')
        operationMode = 'view'
    else:
        selectedPollTemplateName = request.POST.get('template', 'Default template')
        operationMode = request.POST.get('mode', 'save')
    errorMessage = ''

    if operationMode == 'save':
        LMACPollPostTemplateModel.saveTemplate(
            name=request.POST.get('name', ''),
            title=request.POST.get('title', ''),
            body=request.POST.get('body', ''),
            tags=request.POST.get('tags', []),
            category=request.POST.get('category', ''),
            beneficiaries=request.POST.get('beneficiaries', [])
        )
    elif operationMode == 'delete' and request.POST.get('name', '') != 'Default template':
        LMACPollPostTemplateModel.deleteTemplate(
            name=request.POST.get('name', '')
        )

    postTemplates = LMACPollPostTemplateModel.loadTemplates()
    postTemplate = postTemplates[0]
    for iteratedTemplate in postTemplates:
        if iteratedTemplate['name'] == selectedPollTemplateName:
            postTemplate = iteratedTemplate
            break

    return render(request, 'lmacPollsCreatePoll.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lmac-polls'),
            'errorMessage': errorMessage,
            'title': pageTitleHelper('Create a poll')
        },
        'postTemplate': postTemplate,
        'postTemplates': postTemplates,
    })


def _lmacPollLoadUserVotesCommand(username, authorPerm):
    """
    _lmac poll load user votes command.
    
    :param username: Username.
    :param authorPerm: Author perm.

    :return: No return.
    """
    votes = LMACPollModel.loadPollForUser(username, authorPerm)
    if votes == None:
        return {
            'success': False,
            'errorMessage': 'Failed loading votes for this user.'
        }

    return {
        'success': True,
        'command': 'loadUserVotes',
        'votes': votes
    }


def lmacPollAjaxCommand(request: HttpRequest):
    """
    Lmac poll ajax command.
    
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
    print(commandData)
    if commandData['command'] == 'loadUserVotes':
        return JsonResponse(
            _lmacPollLoadUserVotesCommand(
                commandData['parameters']['username'],
                commandData['parameters']['pollPostPermlink']
            )
        )

    return JsonResponse(
        {
            'success': False,
            'errorMessage': 'Command not available.'
        }
    )
