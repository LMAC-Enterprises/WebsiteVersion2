"""
Views.
By quantumg.
"""

from django.http import HttpRequest, Http404
from django.shortcuts import render


# Create your views here.
from LMACGalleryWebProject.core.generalSiteTools import pageTitleHelper, mainMenuHelper
from lmacWinners.models import LMACWinnersModel


def _lmacWinnersMakeContestPaginationDict(contestIds: list, currentContestId: int) -> dict:
    """
    _lmac winners make contest pagination dict.
    
    :param contestIds: (list) Contest ids.
    :param currentContestId: (int) Current contest id.

    :return: Returns a dict.
    """
    contests = len(contestIds)

    if contests == 0:
        return {
            'backward': [],
            'forward': [],
            'current': currentContestId
        }

    paginationBackward = []
    paginationForward = []

    index = contestIds.index(currentContestId)
    print(index)
    if index > 0:
        backRange = index - 4
        if backRange < 0:
            backRange = 0
        for lookBackIndex in range(index - 1, backRange, -1):
            paginationBackward.append(contestIds[lookBackIndex])

    if index < contests - 1:
        aheadRange = index + 4
        if aheadRange > contests -1:
            aheadRange = index + (contests - index)

        for lookAheadIndex in range(index + 1, aheadRange, 1):
            paginationForward.append(contestIds[lookAheadIndex])

    paginationBackward.reverse()

    return {
        'backward': paginationBackward,
        'forward': paginationForward,
        'current': currentContestId,
        'last': contestIds[-1],
        'first': contestIds[0]
    }


def lmacWinnersView(request: HttpRequest, contestId: int = 0):
    """
    Lmac winners view.
    
    :param request: (HttpRequest) Request.
    :param contestId: (int = 0) Contest id.

    :return: No return.
    """

    contest = LMACWinnersModel.loadContest(contestId)
    if not contest:
        raise Http404("Contest not found.")

    print(contest)

    return render(request, 'lmacWinnersPage.html', {
        'overall': {
            'mainMenu': mainMenuHelper('lmac-winner'),
            'errorMessage': '',
            'title': pageTitleHelper('Winners of round ' + str(contest['contestId']))
        },
        'contest': contest,
        'pagination': _lmacWinnersMakeContestPaginationDict(
            LMACWinnersModel.loadAvailableContests(),
            contest['contestId']
        )
    })
