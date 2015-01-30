from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import TestCase
from taskstack_core import manager


class MemberTestCase(TestCase):
    def test_member_manager_user_creation(self):
        manager.create_member(username='John', email='john@example.com', password="john1234")
        user = User.objects.get(username='John')
        self.assertEqual(user.email, 'john@example.com')

    def test_user_does_not_exist(self):
        self.assertRaises(ObjectDoesNotExist, lambda: User.objects.get(username='Cartman'))

    def test_cannot_create_duplicate_user(self):
        try:
            manager.create_member(username='John', email='john@example.com', password="john1234")
            manager.create_member(username='John', email='john@example.com', password="john1234")
        except IntegrityError:
            pass
        
        self.assertEqual(User.objects.count(), 1)


class QueueTestCase(TestCase):
    def setUp(self):
        pass
        #queue = Queue()
        #queue.user =