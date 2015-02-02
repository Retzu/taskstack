from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase
from taskstack_core import manager
from taskstack_core.exceptions import QueueFullException
from taskstack_core.models import Queue, Task, Member


class MemberTestCase(TestCase):
    def test_member_manager_user_creation(self):
        """Test if we can create a user using the manager."""
        manager.create_member(username='John', email='john@example.com', password="john1234")
        user = User.objects.get(username='John')
        self.assertEqual(user.email, 'john@example.com')
        self.assertIsInstance(user.member.queue, Queue)

    def test_user_does_not_exist(self):
        """Test if we can find a non-existent user."""
        self.assertRaises(ObjectDoesNotExist, lambda: User.objects.get(username='Cartman'))

    def test_cannot_create_duplicate_user(self):
        """Test if we can create the same user twice using the manager."""
        try:
            manager.create_member(username='John', email='john@example.com', password="john1234")
            manager.create_member(username='John', email='john@example.com', password="john1234")
        except IntegrityError:
            pass
        
        self.assertEqual(User.objects.count(), 1)


class QueueTestCase(TestCase):
    def setUp(self):
        member = manager.create_member(username='John', email='john@example.com', password='john1234')
        for i in range(10):
            member.queue.add_task(Task(title='Task #{}'.format(i), text='Task #1'.format(i)))

    def test_queue_limit(self):
        """Test if we can go over a queue's task limit."""
        member = Member.objects.get(user__username='John')
        self.assertEqual(member.queue.task_set.count(), 10)

        try:
            member.queue.add_task(Task(title='Task #11', text='This task should not be accepted'))
        except QueueFullException:
            pass

        self.assertEqual(member.queue.task_set.count(), 10)