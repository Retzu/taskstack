"""Unit Tests"""
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase
from taskstack_core import manager
from taskstack_core.exceptions import QueueFullException
from taskstack_core.models import Queue, Task, Member


class MemberTestCase(TestCase):

    """Test user creation/deletion"""

    def test_manager_create_user(self):
        """Test if we can create a user using the manager."""
        member = manager.create_member(email='john@example.com', password="john1234", name="John Doe")
        found_member = Member.objects.get(user__email='john@example.com')
        self.assertEqual(member, found_member)
        self.assertIsInstance(member.queue, Queue)

    def test_user_does_not_exist(self):
        """Test if we can find a non-existent user."""
        self.assertRaises(ObjectDoesNotExist, lambda: Member.objects.get(user__username='Cartman'))

    def test_duplicate_user(self):
        """Test if we can create the same user twice using the manager."""
        try:
            manager.create_member(email='john@example.com', password="john1234", name="John Doe")
            manager.create_member(email='john@example.com', password="john1234", name="John Doe")
        except IntegrityError:
            pass

        self.assertEqual(User.objects.count(), 1)


class QueueTestCase(TestCase):

    """Test messings with queues"""

    def setUp(self):
        member = manager.create_member(email='john@example.com', password='john1234', name="John Doe")
        for i in range(10):
            member.queue.add_task(Task(title='Task #{}'.format(i), text='Task #{}'.format(i)))

    def test_queue_limit(self):

        """Test if we can go over a queue's task limit."""

        member = Member.objects.get(user__username='john@example.com')
        self.assertEqual(member.queue.task_set.count(), 10)

        try:
            member.queue.add_task(Task(title='Task #11', text='This task should not be accepted'))
        except QueueFullException:
            pass

        self.assertEqual(member.queue.task_set.count(), 10)

