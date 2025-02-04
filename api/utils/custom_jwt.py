from typing import Optional

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext as _


def jwt_token_with_extra_kwargs(user):
    """ return RefreshToken instance, with additional kwargs (attributes) """
    token = RefreshToken.for_user(user)
    token['is_staff'] = user.is_staff
    token['first_name'] = user.first_name
    token['last_name'] = user.last_name
    token['email'] = user.email
    token['groups'] = [
        acg.name for acg in user.groups.all()
    ]
    token['is_superuser'] = user.is_superuser
    return token


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            return None

        raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        user = self.get_user(validated_token)

        return user, validated_token

    def get_header(self, request):
        auth_header = request.headers.get('Authorization')

        if auth_header is None:
            return None

        parts = auth_header.split()

        if len(parts) == 1:
            raise AuthenticationFailed(_('Invalid token header. No credentials provided.'))

        elif len(parts) > 2:
            raise AuthenticationFailed(_('Invalid token header. Token string should not contain spaces.'))

        return auth_header

    def get_raw_token(self, header: bytes) -> Optional[bytes]:
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0].lower() != 'token':
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                _("Authorization header must contain two space-delimited values"),
                code="bad_authorization_header",
            )

        return parts[1]
