from rest_framework import viewsets
from rest_framework.response import Response


from users.serializers import UserSerializer, SmallUserSerializer
from users.models import User
from rest_framework.authtoken.models import Token


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View public details of a user.

    User listing is not allowed for privacy reasons.

    View more/private details of the current logged-in user with <a href="/api/me">/api/me</a>
    """
    queryset = User.objects.all()
    serializer_class = SmallUserSerializer
    lookup_field = 'netid'

    def list(self, *args, **kwargs):
        return Response({
            'detail': 'User listing is forbidden.',
            'hint': 'Use /api/users/<netid> to view a user detail or /api/me to view your details'
        }, status=403)


class Me(viewsets.ViewSet):
    """
    View details on the current logged-in user.
    """

    def list(self, request, format=None):
        token, created = Token.objects.get_or_create(user=request.user)

        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
