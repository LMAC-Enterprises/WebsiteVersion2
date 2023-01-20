from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.
from LMACGalleryWebProject.core.MainMenu import mainMenuHelper
from lmacPoll.models import LMACPollModel, LMACPollPostTemplateModel


def lmacPollMainAppView(request: HttpRequest):

    errorMessage = ''
    polls = LMACPollModel.loadPolls()
    if not polls:
        errorMessage = 'Internal error. Please contact the admin.'

    return render(request, 'lmacPollsMain.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lmac-polls'),
            'errorMessage': errorMessage
        },
        'polls': polls
    })


def lmacPollView(request: HttpRequest, author: str = '', permlink: str = ''):

    if len(author) == 0 or len(permlink) == 0:
        return HttpResponse(status=404, content='Sorry, couldn\'t find poll post.')

    errorMessage = ''
    poll = LMACPollModel.loadPoll('@%s/%s' % (author, permlink))
    if not poll:
        errorMessage = 'Failed loading poll post.'

    return render(request, 'lmacPoll.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lmac-polls'),
            'errorMessage': errorMessage
        },
        'poll': poll
    })


def lmacPollCreatePollView(request: HttpRequest):
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

    print(postTemplates)
    print(postTemplate)

    return render(request, 'lmacPollsCreatePoll.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lmac-polls'),
            'errorMessage': errorMessage
        },
        'postTemplate': postTemplate,
        'postTemplates': postTemplates,
    })