"""This module contains helper methods for doing things in taskstack"""
from django.contrib.auth.models import User
from core.models import Member, Queue
from django.db import transaction


def create_member(email, password, name=None, group=None):
    """Creates a new user, adds a Member object and sets an optional group"""
    with transaction.atomic():
        member = Member(name=name, group=group)

        user = User.objects.create_user(username=email, email=email, password=password)
        member.user = user

        member.save()

        queue = Queue(member=member)
        queue.save()

        member.save()
    return member

