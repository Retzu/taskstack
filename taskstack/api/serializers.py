from rest_framework import serializers
from core.models import Group, Member, Queue, Task


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'taskmasters', 'members')
        read_only_fields = ('id', 'taskmasters', 'members')


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member


class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
