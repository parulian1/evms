from autoslug import AutoSlugField

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


def get_username(instance):
    """ Used for auto-slug functionality -- returns the username portion of
    the user's specified email address.
    """
    return instance.email.split('@')[0]


class CustomUserManager(UserManager):
    """
    Same as the basic user manager, but removes the requirement for providing
    'username' (We auto generate that from the user's email address)
    """

    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_guest', False)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def _create_guest(self, email, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_guest(self, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_guest', True)
        # extra_fields.setdefault('site', Site.objects.get_current())
        return self._create_guest(email, **extra_fields)


# Create your models here.
class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    username = AutoSlugField(populate_from=get_username, blank=True, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(
        _('phone number'),
        max_length=25,
        blank=True
    )
    is_guest = models.BooleanField(_('guest'), default=True)

    objects = CustomUserManager()


class Profile(models.Model):
    """
        Additional user profile data.
    """

    class Gender(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        NOT_SPECIFIED = '', _('Prefer Not to Say')

    class MaritalStatus(models.TextChoices):
        married = 'married', _('Married')
        single = 'single', _('Single')

    country = models.CharField(max_length=150, blank=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    gender = models.CharField(
        choices=Gender.choices,
        max_length=10,
        blank=True,
        default=Gender.NOT_SPECIFIED
    )
    occupation = models.CharField(max_length=90, blank=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='profile',
        on_delete=models.CASCADE
    )
    marital_status = models.CharField(
        choices=MaritalStatus.choices,
        max_length=10,
        blank=True,
        default=MaritalStatus.single
    )

    def get_full_name(self):
        return self.user.get_full_name()






