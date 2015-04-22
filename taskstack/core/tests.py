"""Unit Tests"""
from unittest import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import Client
from core.exceptions import QueueFullException
from core.models import Queue, Task, Member, Group


class MemberTestCase(TestCase):

    """Test user creation/deletion."""

    def test_manager_create_user(self):
        """Test if we can create a user using the manager."""
        member = Member.create(email='john1@example.com', password='john1234', name='John Doe')
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
            Member.create(email='john2@example.com', password='john1234', name='John Doe')
            Member.create(email='john2@example.com', password='john1234', name='John Doe')

    def test_delete_user(self):
        john = Member.create(email='john3@example.com', password='john1234', name='John Doe')
        self.assertIsNotNone(Member.objects.get(user__email='john3@example.com'))
        john.delete()
        with self.assertRaises(ObjectDoesNotExist):
            where_are_you_john = Member.objects.get(user__email='john3@example.com')


class GroupTestCase(TestCase):

    """Test groups."""

    def test_groups(self):
        """Test if a group can hold members."""
        group = Group.objects.create(name="Test Group")

        # Create 10 users
        users = []
        for i in range(10):
            users.append(
                Member.create(email='user{}@example.com'.format(i),
                              password='password',
                              name='User #{}'.format(i),
                              group=group)
            )

        self.assertEqual(group.members.count(), 10)


class QueueTestCase(TestCase):

    """Test messings with queues."""

    def test_queue_limit(self):
        """Test if we can go over a queue's task limit."""
        # First fill the queue with as many tasks it can hold
        member = Member.create(email='john4@example.com', password='john1234', name='John Doe')
        for i in range(member.queue.limit):
            member.queue.add_task(Task(title='Task #{}'.format(i), text='Task #{}'.format(i)))

        member = Member.objects.get(user__username='john4@example.com')
        self.assertEqual(member.queue.tasks.count(), member.queue.limit)

        # Add a another task and expect an exception
        with self.assertRaises(QueueFullException):
            member.queue.add_task(Task(title='Task #11', text='This task should not be accepted'))

        self.assertEqual(member.queue.tasks.count(), member.queue.limit)


class PermissionTestCase(TestCase):

    """Test permissions."""

    def test_queue_permissions(self):
        john = Member.create(email='john5@example.com', password='john1234', name='John Doe')
        jane = Member.create(email='jane5@example.com', password='jane1234', name='Jane Doe')

        self.assertTrue(john.has_perm('add_to_queue', john.queue))
        self.assertTrue(jane.has_perm('add_to_queue', jane.queue))
        self.assertTrue(john.has_perm('remove_from_queue', john.queue))
        self.assertTrue(jane.has_perm('remove_from_queue', jane.queue))

        self.assertFalse(john.has_perm('add_to_queue', jane.queue))
        self.assertFalse(jane.has_perm('add_to_queue', john.queue))
        self.assertFalse(john.has_perm('remove_from_queue', jane.queue))
        self.assertFalse(jane.has_perm('remove_from_queue', john.queue))

    def test_taskmaster(self):
        group = Group.objects.create(name="My Group #1")
        taskmaster = Member.create(email='taskmaster@example.com', password='taskmaster', name='Taskmaster')

        john = Member.create(email='john6@example.com', password='john1234', name='John Doe', group=group)
        jane = Member.create(email='jane6@example.com', password='jane1234', name='Jane Doe', group=group)

        group.add_taskmaster(taskmaster)

        self.assertTrue(taskmaster.has_perm('add_to_queue', john.queue))
        self.assertTrue(taskmaster.has_perm('add_to_queue', jane.queue))

        group.remove_taskmaster(taskmaster)

        self.assertFalse(taskmaster.has_perm('add_to_queue', john.queue))
        self.assertFalse(taskmaster.has_perm('add_to_queue', jane.queue))


class WebInterfaceTestCase(TestCase):

    """Test the web frontend."""

    def test_index(self):
        """Test if the index returns *something*."""
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)