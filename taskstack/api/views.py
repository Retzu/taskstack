from api.serializers import GroupSerializer
from core.models import Group
from rest_framework import mixins
from rest_framework import generics


class GroupDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)