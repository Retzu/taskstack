"""Unit Tests"""
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import Client
from unittest import TestCase
from core import manager
from core.exceptions import QueueFullException
from core.models import Queue, Task, Member


class MemberTestCase(TestCase):

    """Test user creation/deletion"""

    def test_manager_create_user(self):
        """Test if we can create a user using the manager."""
        member = manager.create_member(email='john1@example.com', password="john1234", name="John Doe")
        found_member = Member.objects.get(user__email='john1@example.com')
        self.assertEqual(member, found_member)
        self.assertIsInstance(member.queue, Queue)

    def test_user_does_not_exist(self):
        """Test if we can find a non-existent user."""
        with self.assertRaises(ObjectDoesNotExist):
            Member.objects.get(user__username='Cartman')

    def test_duplicate_user(self):
        """Test if we can create the same user twice using the manager."""
        with self.assertRaises(IntegrityError):
            manager.create_member(email='john2@example.com', password="john1234", name="John Doe")
            manager.create_member(email='john2@example.com', password="john1234", name="John Doe")

        self.assertEqual(User.objects.count(), 1)


class QueueTestCase(TestCase):

    """Test messings with queues"""

    def test_queue_limit(self):
        """Test if we can go over a queue's task limit."""
        # First fill the queue with as many tasks it can hold
        member = manager.create_member(email='john@example.com', password='john1234', name="John Doe")
        for i in range(member.queue.limit):
            member.queue.add_task(Task(title='Task #{}'.format(i), text='Task #{}'.format(i)))

        member = Member.objects.get(user__username='john@example.com')
        self.assertEqual(member.queue.task_set.count(), member.queue.limit)

        # Add a another task and expect an exception
        with self.assertRaises(QueueFullException):
            member.queue.add_task(Task(title='Task #11', text='This task should not be accepted'))

        self.assertEqual(member.queue.task_set.count(), member.queue.limit)


class WebInterfaceTestCase(TestCase):

    """Test the web frontend."""

    def test_index(self):
        """Test if the index returns *something*."""
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)