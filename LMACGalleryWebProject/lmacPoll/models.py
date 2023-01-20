import datetime
import json
import re
from typing import Optional
from urllib.parse import urlparse

from beem.comment import Comment
from beem.exceptions import OfflineHasNoRPCException
from django.core.cache import cache
from django.db import models
from beem.discussions import Query, Discussions, Discussions_by_created


# Create your models here.
class LMACPollModel:
    LIMIT_POLL_SEARCH_TO_USERS = ['lmac', 'shaka', 'quantumg', 'agmoore', 'mballesteros']
    CACHE_TIME_IN_SECONDS = 3600

    @staticmethod
    def loadPolls() -> Optional[list]:

        cached = cache.get('lmac_polls')
        if cached is not None:
            return cached

        query = Query(limit=51, tag="lmacpoll")

        dateTimeNow = datetime.datetime.now(datetime.timezone.utc)
        polls = []
        try:
            for comment in Discussions_by_created(query):

                if comment.author not in LMACPollModel.LIMIT_POLL_SEARCH_TO_USERS:
                    continue

                endsIn = 'Poll is closed!'
                hours = int((dateTimeNow - comment['created']).total_seconds() / 3600)
                if hours <= 24:
                    endsIn = "Ends in %s hours." % hours

                polls.append(
                    {
                        'title': comment.title,
                        'authorperm': comment.authorperm,
                        'endsIn': endsIn
                    }
                )
        except OfflineHasNoRPCException:
            return None

        cache.set('lmac_polls', polls,  LMACPollModel.CACHE_TIME_IN_SECONDS)

        return polls

    @staticmethod
    def loadPoll(authorperm: str) -> Optional[dict]:

        sid = 'lmac_poll_' + authorperm
        cached = cache.get(sid)
        if cached is not None:
            return cached

        try:
            comment = Comment(authorperm)
        except OfflineHasNoRPCException:
            return None

        poll = {
            'title': comment.title,
            'options': LMACPollModel._parseOptions(comment)
        }

        cache.set(sid, poll, 300)

        return poll

    @staticmethod
    def _parseOptions(comment) -> Optional[list]:

        matches = re.finditer(
            r"(@[a-zA-Z0-9\.\-]+): \[-> Original post\]\((https\:\/\/.*)\)\s+\!\[\]\((https\:\/\/.*)\)",
            comment.body,
            re.MULTILINE
        )

        options = {}
        for match in matches:
            authorperm = urlparse(match[2]).path
            if authorperm[0] == '/':
                authorperm = authorperm[1:]

            options[match[1]] = {
                'author': match[1],
                'post': authorperm,
                'image': match[3],
                'commentAuthorReference': '',
                'commentPermlinkReference': ''
            }

        for subComment in comment.get_replies(raw_data=False):
            if subComment['author'] != comment['author']:
                continue
            authorReference = subComment['body'].strip()
            if authorReference in options.keys():
                rewards = 0.0
                if "pending_payout_value" in subComment:
                    rewards += subComment["pending_payout_value"].amount if not isinstance(subComment["pending_payout_value"], str) else float(subComment["pending_payout_value"].split(' ')[0])
                if "curator_payout_value" in subComment:
                    rewards += subComment["curator_payout_value"].amount if not isinstance(subComment["curator_payout_value"], str) else float(subComment["curator_payout_value"].split(' ')[0])
                if "author_payout_value" in subComment:
                    rewards += subComment["author_payout_value"].amount if not isinstance(subComment["author_payout_value"], str) else float(subComment["author_payout_value"].split(' ')[0])

                options[authorReference]['votes'] = len(subComment.get_votes(raw_data=True))
                options[authorReference]['rewards'] = rewards
                options[authorReference]['commentAuthorReference'] = subComment['author']
                options[authorReference]['commentPermlinkReference'] = subComment['permlink']

        return list(options.values())

    @staticmethod
    def loadUserVotes(username: str) -> dict:
        pass


class LMACPollPostTemplateModel(models.Model):
    class Meta:
        db_table = 'poll_post_template'
        verbose_name = 'Poll Post Template'
        managed = True
        permissions = [
            (
                "manage poll post templates",
                "Allows to manage poll post templates."
            )
        ]

    name = models.CharField(max_length=256, primary_key=True)
    title = models.CharField(max_length=256)
    tags = models.CharField(max_length=256)
    category = models.CharField(max_length=256, default='hive-1746952')
    body = models.TextField()
    beneficiaries = models.TextField()

    @staticmethod
    def loadTemplates():

        templates = LMACPollPostTemplateModel.objects.all()

        templateInfos = [
            {
                'name': 'Default template',
                'title': 'Post title',
                'body': '# Final Poll\n\n{nominees}\n',
                'tags': 'letsmakeacollage lil art collage photography lmacpoll',
                'category': 'hive-174695',
                'beneficiaries': []
            }
        ]
        for template in templates:
            templateInfos.append(
                {
                    'name': template.name,
                    'title': template.title,
                    'body': template.body,
                    'tags': template.tags,
                    'category': template.category,
                    'beneficiaries': json.loads(template.beneficiaries)
                }
            )

        return templateInfos

    @staticmethod
    def saveTemplate(name: str, title: str, body: str, tags: list, category: str, beneficiaries: list):
        LMACPollPostTemplateModel.objects.update_or_create(
            name=name,
            defaults={
                'title': title,
                'body': body,
                'tags': json.dumps(tags),
                'category': category,
                'beneficiaries': json.dumps(beneficiaries)
            }
        )

    @staticmethod
    def deleteTemplate(name):
        LMACPollPostTemplateModel.objects.delete(name=name)
