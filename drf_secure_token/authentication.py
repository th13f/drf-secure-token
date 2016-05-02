from django.conf import settings
from django.utils import timezone

from rest_framework.authentication import TokenAuthentication

from rest_framework import exceptions
from django.utils.translation import ugettext_lazy as _

from drf_secure_token.models import Token


TOKEN_AGE = getattr(settings, 'TOKEN_AGE', None)
UPDATE_TOKEN = getattr(settings, 'UPDATE_TOKEN', True)


class SecureTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.select_related('user').get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if TOKEN_AGE:
            if (UPDATE_TOKEN and token.dead_in < timezone.now()) or (not UPDATE_TOKEN and token.expire_in < timezone.now()):
                token.delete()
                raise exceptions.AuthenticationFailed(_('Token has expired.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)
