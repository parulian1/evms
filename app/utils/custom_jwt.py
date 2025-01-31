from typing import Optional
from rest_framework_simplejwt.authentication import JWTAuthentication, AUTH_HEADER_TYPE_BYTES
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext as _


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
