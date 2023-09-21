"""
Models.
By quantumg.
"""

import json
from typing import Optional

from django.core.cache import cache
from django.db import models, transaction


# Create your models here.
class LMACWinnersModel(models.Model):
    """
    TODO: Needs description!
    """
    class Meta:
        db_table = 'lmac_contests'
        managed = True
        verbose_name = 'LMAC Contests'
        app_label = 'lmacWinners'

    contestId = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=512)
    postUrl = models.CharField(max_length=512)
    templateImageUrl = models.CharField(max_length=512)
    winners = models.TextField()
    isVisible = models.BooleanField(default=True)

    @staticmethod
    def loadAvailableContests() -> list:
        """
        Load available contests.
        

        :return: Returns a list.
        """
        contests = LMACWinnersModel.objects.all().order_by('contestId').values('contestId')
        if not contests:
            return []

        contestIds = []
        for contest in contests:
            contestIds.append(contest['contestId'])

        return contestIds

    @staticmethod
    def loadContest(contestId: int = 0) -> Optional[dict]:
        """
        Load contest.
        
        :param contestId: (int = 0) Contest id.

        :return: Optional of "dict".
        """

        if contestId > 0:

            contest = LMACWinnersModel.objects.filter(contestId=contestId, isVisible=True).first()
        else:
            contest = LMACWinnersModel.objects.all().order_by('-contestId').first()

        if not contest:
            return None

        return {
            'contestId': contest.contestId,
            'title': contest.title,
            'postUrl': contest.postUrl,
            'templateImageUrl': contest.templateImageUrl,
            'winners': json.loads(contest.winners).values(),
        }

    @staticmethod
    def addContestOutcomes(outcomes: list):
        """
        Add contest outcomes.
        
        :param outcomes: (list) Outcomes.

        :return: No return.
        """
        with transaction.atomic():
            for outcome in outcomes:
                winnersObj = LMACWinnersModel(
                    contestId=outcome['contestId'],
                    title=outcome['title'],
                    postUrl=outcome['postUrl'],
                    templateImageUrl=outcome['templateImageUrl'],
                    winners=json.dumps(outcome['winners']),
                    isVisible=True
                )
                winnersObj.save()

    @staticmethod
    def getLastContestWinnerCollages() -> list[dict[str, str]]:
        """
        Get last contest winner collages.
        

        :return: Returns a list of "dic".
        """
        sid = 'lmac_last_contest_winner_collages'
        cached = cache.get(sid)
        if cached is not None:
            return cached

        winnerEntities = json.loads(
            LMACWinnersModel.objects.filter(isVisible=True).order_by('-contestId').first().winners
        )

        winnersUnsorted = []
        for winnerEntity in winnerEntities.values():
            winnersUnsorted.append(
                {
                    'name': winnerEntity['artist'],
                    'winningPlace': winnerEntity['winningPlace'],
                    'url': winnerEntity['imageUrl']
                }
            )

        winnersSorted = sorted(winnersUnsorted, key=lambda d: d['winningPlace'])

        for winnerEntity in winnersSorted:
            if 'winningPlace' in winnerEntity:
                del winnerEntity['winningPlace']

        cache.set(sid, winnersSorted, 14400)

        return winnersSorted
