import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

import requests


class HiveInfo:
    hiveNodes = [
        'https://api.hive.blog',
        'https://api.openhive.network',
        'https://anyx.io',
        'https://hived.privex.io',
        'https://rpc.ausbit.dev',
        'https://techcoderx.com',
        'https://hived.emre.sh',
        'https://api.deathwing.me',
        'https://api.c0ff33a.uk'
    ]

    @staticmethod
    def elapsedTime(timeInput) -> str:
        seconds = (datetime.utcnow() - datetime.fromisoformat(timeInput)).total_seconds()

        minutes = int(seconds / 60)
        hours = int(minutes / 60)
        days = int(hours / 24)
        weeks = int(days / 7)
        month = int(weeks / 4)

        if minutes < 1:
            return f'{seconds} seconds ago'
        if hours < 1:
            return f'{minutes} minutes ago'
        if days < 1:
            return f'{hours} hours ago'
        if weeks < 1:
            return f'{days} days ago'
        if month < 1:
            return f'{weeks} weeks ago'

        return f'{month} month ago'


class HiveAPIRequest(ABC):
    def __init__(self, method: str, params: list, nodeUrls: list = None):
        self._rpcDict = {
            'jsonrpc': "2.0",
            'method': method,
            'params': params,
            'id': 1
        }
        self._nodeUrls = nodeUrls if nodeUrls is not None else HiveInfo.hiveNodes

    def _loadResponse(self) -> any:
        response = None

        for nodeUrl in self._nodeUrls:
            try:
                response = requests.post(
                    nodeUrl,
                    json=self._rpcDict
                )
            except requests.ConnectionError:
                continue
            except requests.Timeout:
                continue
            except requests.exceptions.HTTPError:
                continue

            break

        if response is None:
            return None

        responseData = response.json()
        if 'error' in responseData:
            return None

        return responseData['result']

    @abstractmethod
    def submit(self) -> any:
        pass


class HiveComment:
    def __init__(self, commentDict: dict):
        self._author = commentDict['author']
        self._permlink = commentDict['permlink']
        self._title = commentDict['title']
        self._body = commentDict['body']
        self._category = commentDict['category']
        self._created = datetime.fromisoformat(commentDict['created']).replace(tzinfo=timezone.utc)
        self._updated = datetime.fromisoformat(commentDict['last_update']).replace(tzinfo=timezone.utc)
        self._lastPayout = datetime.fromisoformat(commentDict['last_payout']).replace(tzinfo=timezone.utc)
        self._cashOutTime = datetime.fromisoformat(commentDict['cashout_time']).replace(tzinfo=timezone.utc)
        self._elapsed = HiveInfo.elapsedTime(commentDict['created'])
        self._votes = commentDict['active_votes']
        self._jsonMetaData = json.loads(commentDict['json_metadata'])
        self._tags = []
        self._commentDict = commentDict
        self._replies = commentDict['replies']

        if 'tags' in self._jsonMetaData:
            self._tags = self._jsonMetaData['tags']

    @property
    def elapsed(self) -> str:
        return self._elapsed

    @property
    def rewards(self) -> float:
        rewards = 0.0
        if "pending_payout_value" in self._commentDict:
            rewards += self._commentDict["pending_payout_value"].amount \
                if not isinstance(self._commentDict["pending_payout_value"], str) else float(
                self._commentDict["pending_payout_value"].split(' ')[0])
        if "curator_payout_value" in self._commentDict:
            rewards += self._commentDict["curator_payout_value"].amount \
                if not isinstance(self._commentDict["curator_payout_value"], str) else float(
                self._commentDict["curator_payout_value"].split(' ')[0])
        if "author_payout_value" in self._commentDict:
            rewards += self._commentDict["author_payout_value"].amount \
                if not isinstance(self._commentDict["author_payout_value"], str) else float(
                self._commentDict["author_payout_value"].split(' ')[0])

        return rewards

    @property
    def author(self) -> str:
        return self._author

    @property
    def tags(self) -> list:
        return self._tags

    @property
    def title(self) -> str:
        return self._title

    @property
    def body(self) -> str:
        return self._body

    @property
    def category(self) -> str:
        return self._category

    @property
    def created(self) -> datetime:
        return self._created

    @property
    def updated(self) -> datetime:
        return self._updated

    @property
    def lastPayout(self) -> datetime:
        return self._lastPayout

    @property
    def cashOutTime(self) -> datetime:
        return self._cashOutTime

    @property
    def votes(self) -> list:
        return self._votes

    @property
    def authorPerm(self) -> str:
        return f'@{self._author}/{self._permlink}'

    @property
    def permlink(self) -> str:
        return self._permlink

    @property
    def jsonMetaData(self) -> any:
        return self._jsonMetaData

    def getReplies(self) -> list["HiveComment"]:
        request = HiveCommentRepliesRequest(self.authorPerm)
        response = request.submit()
        if response is None:
            return []

        return response

    @property
    def replyCount(self) -> int:
        return len(self._replies)

    def coverImage(self) -> str:

        if 'image' not in self.jsonMetaData.keys():
            return '/static/images/defaultImage.png'

        if len(self.jsonMetaData['image']) == 0:
            return '/static/images/defaultImage.png'

        return 'https://images.hive.blog/800x0/{url}'.format(url=self.jsonMetaData['image'][0])


class HiveCommentRepliesRequest(HiveAPIRequest):
    def __init__(self, authorPerm: str, nodeUrls: list = None):
        super().__init__(
            'condenser_api.get_content_replies',
            HiveCommentRequest.splitAuthorPerm(authorPerm),
            nodeUrls
        )

    @staticmethod
    def splitAuthorPerm(authorPerm: str) -> list:
        if authorPerm.startswith('@'):
            authorPerm = authorPerm[1:]

        return authorPerm.split('/')

    def submit(self) -> Optional[list[HiveComment]]:
        responseData = self._loadResponse()
        if responseData is None:
            return None

        comments = []
        for commentData in responseData:
            comments.append(
                HiveComment(commentData)
            )

        return comments


class HiveCommentRequest(HiveAPIRequest):
    def __init__(self, authorPerm: str, nodeUrls: list = None):
        super().__init__(
            'condenser_api.get_content',
            HiveCommentRequest.splitAuthorPerm(authorPerm),
            nodeUrls
        )
        self._authorPerm = authorPerm

    @staticmethod
    def splitAuthorPerm(authorPerm: str) -> list:
        if authorPerm.startswith('@'):
            authorPerm = authorPerm[1:]

        return authorPerm.split('/')

    def submit(self) -> Optional[HiveComment]:
        responseData = self._loadResponse()
        if responseData is None:
            return None

        return HiveComment(responseData)


class HiveDiscussionsByCreatedRequest(HiveAPIRequest):
    def __init__(self, tag: str, limit: int = 100, nodeUrls: list = None):
        super().__init__(
            'condenser_api.get_discussions_by_created',
            [{'tag': tag, 'limit': limit}],
            nodeUrls
        )

    def submit(self) -> Optional[list[HiveComment]]:
        responseData = self._loadResponse()
        if responseData is None:
            return None

        hiveComments = []

        for discussion in responseData:
            hiveComments.append(
                HiveComment(discussion)
            )

        return hiveComments


class HiveAccountPostsRequest(HiveAPIRequest):
    def __init__(self, accountName: str, limit: int = 100, nodeUrls: list = None):
        super().__init__(
            'condenser_api.get_discussions_by_author_before_date',
            [
                accountName,
                "",
                datetime.utcnow().isoformat(),
                limit
            ],
            nodeUrls
        )

    def submit(self) -> Optional[list[HiveComment]]:
        responseData = self._loadResponse()
        if responseData is None:
            return None

        hiveComments = []

        for discussion in responseData:
            hiveComments.append(
                HiveComment(discussion)
            )

        return hiveComments


"""if __name__ == '__main__':
    request = HiveCommentRequest(
        ['https://api.hive.blog'],
        'quantumg',
        'stables-nft-art-en-or-de'
    )
    print(request.submit().authorPerm)
    request = HiveDiscussionsByCreatedRequest('letsmakeacollage')

    for comment in request.submit():
        print(comment.authorPerm)"""

