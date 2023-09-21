"""
Models.
By quantumg.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class LMACAPIAccessModel(models.Model):
    """
    TODO: Needs description!
    """
    MAX_CONTINGENT_PER_DAY = 50

    class Meta:
        db_table = 'LMACAPIAccess'
        verbose_name = 'LMAC API Access'

    _apiKey = models.CharField(primary_key=True, max_length=512, unique=True, db_column='apiKey')
    _contingentLeft = models.IntegerField(db_column='contingentLeft', default=0)

    @property
    def apiKey(self) -> str:
        """
        Api key.
        

        :return: Returns a string.
        """
        return self._apiKey

    @apiKey.setter
    def apiKey(self, value: str):
        """
        Api key.
        
        :param value: (str) Value.

        :return: No return.
        """
        self._apiKey = value

    @property
    def contingentLeft(self) -> int:
        """
        Contingent left.
        

        :return: Returns an integer.
        """
        return self._contingentLeft

    @contingentLeft.setter
    def contingentLeft(self, value: int):
        """
        Contingent left.
        
        :param value: (int) Value.

        :return: No return.
        """
        self._contingentLeft = value

    @staticmethod
    def openContingent(apiKey: str) -> bool:
        """
        Open contingent.
        
        :param apiKey: (str) Api key.

        :return: bool.
        """
        try:
            obj = LMACAPIAccessModel.objects.get(_apiKey=apiKey)
        except ObjectDoesNotExist:
            obj = LMACAPIAccessModel(_apiKey=apiKey, _contingentLeft=LMACAPIAccessModel.MAX_CONTINGENT_PER_DAY)

        if obj.contingentLeft <= 0:
            return False

        obj.contingentLeft -= 1
        obj.save()

        return True

    @classmethod
    def resetContingents(cls):
        """
        Reset contingents.
        

        :return: No return.
        """
        LMACAPIAccessModel.objects.all().update(_contingentLeft=LMACAPIAccessModel.MAX_CONTINGENT_PER_DAY)

