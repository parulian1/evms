import re

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class PhoneNumberValidator:
    def __init__(self, min_length=5, max_length=25):
        self.min_length = min_length
        self.max_length = max_length

    def __call__(self, value):
        if len(value) not in range(self.min_length, self.max_length + 1):
            raise ValidationError(
                'Invalid length Phone number, '
                f'min_length: {self.min_length}, max_length {self.max_length}'
            )

        valid_phone_number = re.search(
            r'(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}$',
            value
        )
        if not valid_phone_number:
            raise ValidationError(_('Invalid Phone number'))
        return value