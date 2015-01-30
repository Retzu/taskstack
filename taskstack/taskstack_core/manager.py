from django.contrib.auth.models import User
from taskstack_core.models import Member
from django.db import transaction


def create_member(username, email, password, group=None):
    """Creates a new user, adds a Member object and sets an optional group"""
    with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            member = Member(user, group)
            member.save()