"""
Models.
By quantumg.
"""

import datetime
import json
import re
from typing import Optional
from urllib.parse import urlparse

from django.core.cache import cache
from django.db import models

# Create your models here.
from LMACGalleryWebProject.core.hiveNetwork import HiveCommentRequest, HiveDiscussionsByCreatedRequest


class LMACPollModel:
    """
    L m a c poll model.
    """
    LIMIT_POLL_SEARCH_TO_USERS = ['lmac', 'shaka', 'quantumg', 'agmoore', 'mballesteros']
    CACHE_TIME_IN_SECONDS = 3600

    @staticmethod
    def loadPolls() -> Optional[list]:
        """
        Load polls.
        

        :return: Optional of "list".
        """

        cached = cache.get('lmac_polls')
        if cached is not None:
            return cached

        dateTimeNow = datetime.datetime.now(datetime.timezone.utc)
        polls = []

        discussionsRequest = HiveDiscussionsByCreatedRequest('lmacpoll')
        discussions = discussionsRequest.submit()
        if discussions is None:
            return None

        for comment in discussions:

            if comment.author not in LMACPollModel.LIMIT_POLL_SEARCH_TO_USERS:
                continue

            endsIn = 'Poll is closed!'
            hours = int((dateTimeNow - comment.created).total_seconds() / 3600)
            if hours <= 24:
                endsIn = "Ends in %s hours." % hours

            polls.append(
                {
                    'title': comment.title,
                    'authorperm': comment.authorPerm,
                    'endsIn': endsIn
                }
            )

        cache.set('lmac_polls', polls,  LMACPollModel.CACHE_TIME_IN_SECONDS)

        return polls

    @staticmethod
    def loadPoll(authorperm: str) -> Optional[dict]:
        """
        Load poll.
        
        :param authorperm: (str) Authorperm.

        :return: Optional of "dict".
        """

        sid = 'lmac_poll_' + authorperm
        cached = cache.get(sid)
        if cached is not None:
            return cached

        request = HiveCommentRequest(authorperm)
        comment = request.submit()
        if comment is None:
            return None

        poll = {
            'title': comment.title,
            'options': LMACPollModel._parseOptions(comment)
        }

        cache.set(sid, poll, 300)

        return poll

    @staticmethod
    def _parseOptions(comment) -> Optional[list]:
        """
        _parse options.
        
        :param comment: Comment.

        :return: Optional of "list".
        """

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

        for subComment in comment.getReplies():
            if subComment.author != comment.author:
                continue
            authorReference = subComment.body.strip()
            if authorReference in options.keys():
                options[authorReference]['votes'] = len(subComment.votes)
                options[authorReference]['rewards'] = subComment.rewards
                options[authorReference]['commentAuthorReference'] = subComment.author
                options[authorReference]['commentPermlinkReference'] = subComment.permlink

        return list(options.values())

    @staticmethod
    def loadUserVotes(username: str) -> dict:
        """
        Load user votes.
        
        :param username: (str) Username.

        :return: Returns a dict.
        """
        pass

    @staticmethod
    def loadPollForUser(username: str, pollPostAuthorPerm: str) -> Optional[dict]:
        """
        Load poll for user.
        
        :param username: (str) Username.
        :param pollPostAuthorPerm: (str) Poll post author perm.

        :return: Optional of "dict".
        """

        request = HiveCommentRequest(pollPostAuthorPerm)
        comment = request.submit()
        if comment is None:
            return None

        votes = {}
        for reply in comment.getReplies():
            for activeVote in reply.votes:
                if username == activeVote['voter']:
                    percent = int(activeVote['percent'])
                    votes[reply.permlink] = percent / 100 if percent > 0 else 0

        return votes


class LMACPollPostTemplateModel(models.Model):
    """
    TODO: Needs description!
    """
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
        """
        Load templates.
        

        :return: No return.
        """

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
        """
        Save template.
        
        :param name: (str) Name.
        :param title: (str) Title.
        :param body: (str) Body.
        :param tags: (list) Tags.
        :param category: (str) Category.
        :param beneficiaries: (list) Beneficiaries.

        :return: No return.
        """
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
        """
        Delete template.
        
        :param name: Name.

        :return: No return.
        """
        LMACPollPostTemplateModel.objects.delete(name=name)
