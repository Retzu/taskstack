from django.contrib.auth.models import User
from taskstack_core.models import Member, Queue
from django.db import transaction


def create_member(username, email, password, group=None):
    """Creates a new user, adds a Member object and sets an optional group"""
    with transaction.atomic():
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        member = Member(user=user, group=group)
        member.save()

        queue = Queue()
        member.queue = queue
        queue.save()