from django.db import models
from django.utils.translation import gettext_lazy as _


class Gender(models.TextChoices):
    MALE = 'male', _('Male')
    FEMALE = 'female', _('Female')
    NOT_SPECIFIED = '', _('Prefer Not to Say')


class MaritalStatus(models.TextChoices):
    MARRIED = 'married', _('Married')
    SINGLE = 'single', _('Single')


class Responsibility(models.TextChoices):
    HOST = 'host', _('Host')
    PARTICIPANT = 'participant', _('Prefer Not to Say')