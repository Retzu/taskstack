"""API views."""
from api.serializers import GroupSerializer, MemberSerializer
from core.exceptions import GroupException
from core.models import Group, Member
from rest_framework import mixins
from rest_framework import generics
from rest_framework import views
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status


class GroupDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):

    """CBV for a single group."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class GroupList(views.APIView):

    """CBV for group lists."""

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            try:
                group = serializer.save()
                group.set_creator(request.user)
                group.save()
                response = Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)
                return response
            except GroupException:
                raise PermissionDenied()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemberDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):

    """CBV for a single member."""

    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


@api_view(['GET'])
def current_user(request):
    return Response(MemberSerializer(request.user).data)