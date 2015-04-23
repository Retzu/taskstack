"""Unit Tests"""
from unittest import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import Client, SimpleTestCase
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
        # test __str__
        self.assertGreater(len(member.__str__()), 0)
        self.assertGreater(len(member.queue.__str__()), 0)
        # test __str__ for member without name
        member = Member.create(email='john_@example.com', password='john1234')
        self.assertGreater(len(member.__str__()), 0)

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
        """Test if we can delete users."""
        john = Member.create(email='john3@example.com', password='john1234', name='John Doe')
        self.assertIsNotNone(Member.objects.get(user__email='john3@example.com'))
        john.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Member.objects.get(user__email='john3@example.com')


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

    """Test messing with queues."""

    def test_queue_limit(self):
        """Test if we can go over a queue's task limit."""
        # First fill the queue with as many tasks it can hold
        member = Member.create(email='john4@example.com', password='john1234', name='John Doe')
        for i in range(member.queue.limit):
            task = Task(title='Task #{}'.format(i), text='Task #{}'.format(i))
            member.queue.add_task(task)
            self.assertGreater(len(task.__str__()), 0)

        member = Member.objects.get(user__username='john4@example.com')
        self.assertEqual(member.queue.tasks.count(), member.queue.limit)

        # Add a another task and expect an exception
        with self.assertRaises(QueueFullException):
            member.queue.add_task(Task(title='Task #11', text='This task should not be accepted'))

        self.assertEqual(member.queue.tasks.count(), member.queue.limit)


class PermissionTestCase(TestCase):

    """Test permissions."""

    def test_queue_permissions(self):
        """Test if members have the right permissions to queues."""
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
        """Test if taskmasters have the right permissions to queues."""
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


class WebInterfaceTestCase(SimpleTestCase):

    """Test the web frontend."""

    def test_index(self):
        """Test if the index returns a redirect to login when not logged in."""
        client = Client()
        response = client.get('/', follow=True)
        self.assertRedirects(response, '/login?next=/')

    def test_registration(self):
        """Test if registrations are working."""
        client = Client()
        response = client.post('/register', data={
            'email': 'test1@example.com',
            'name': 'Testy McGee',
            'password': 'password',
            'password_repeat': 'password'
        }, follow=True)
        self.assertRedirects(response, '/')

        self.assertIsInstance(Member.objects.get(user__email='test1@example.com'), Member)
        self.assertIsInstance(Member.objects.get(user__email='test1@example.com').user, User)

    def test_empty_form(self):
        """Test what happens when form is completely empty."""
        client = Client()
        response = client.post('/register', data={
            'email': '',
            'name': '',
            'password': '',
            'password_repeat': ''
        }, follow=True)
        for field in ['email', 'name', 'password', 'password_repeat']:
            self.assertFormError(response, 'form', field, 'This field is required.')

    def test_invalid_email(self):
        """Test what happens when email field in invalid."""
        client = Client()
        response = client.post('/register', data={
            'email': 'not an email address',
            'name': 'Testy McGee',
            'password': 'password',
            'password_repeat': 'password'
        }, follow=True)
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')

    def test_password_dont_match(self):
        """Test password that don't match."""
        client = Client()
        response = client.post('/register', data={
            'email': 'not an email address',
            'name': 'Testy McGee',
            'password': 'password',
            'password_repeat': 'not matching'
        }, follow=True)
        self.assertFormError(response, 'form', None, 'Passwords don\'t match!')

    def test_user_exists(self):
        """Register existing address.

        Test what happens when somebody tries to register a new user
        when the used email address is already in use.
        """
        client = Client()
        response = client.post('/register', data={
            'email': 'existing@example.com',
            'name': 'Testy McGee',
            'password': 'password',
            'password_repeat': 'password'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(Member.objects.get(user__email='existing@example.com'), Member)

        client.logout()

        response = client.post('/register', data={
            'email': 'existing@example.com',
            'name': 'Totally not Testy McGee',
            'password': 'password',
            'password_repeat': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'User already exists!')

    def test_register_redirect(self):
        """Test if going to /register when logged in redirects to /."""
        client = Client()
        response = client.post('/register', data={
            'email': 'new.user@example.com',
            'name': 'Testy McGee',
            'password': 'password',
            'password_repeat': 'password'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(Member.objects.get(user__email='new.user@example.com'), Member)

        response = client.get('/register')
        self.assertRedirects(response, '/')

    def test_already_logged_in(self):
        """Test if going to /login when logged in redirects to /."""
        client = Client()
        response = client.post('/register', data={
            'email': 'new.user2@example.com',
            'name': 'Testy McGee',
            'password': 'password',
            'password_repeat': 'password'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(Member.objects.get(user__email='new.user2@example.com'), Member)

        response = client.get('/login')
        self.assertRedirects(response, '/')

    def test_login(self):
        """Test if /login works."""
        client = Client()
        response = client.post('/register', data={
            'email': 'test.login@example.com',
            'name': 'Testy McGee',
            'password': 'password',
            'password_repeat': 'password'
        }, follow=True)
        client.logout()

        response = client.post('/login', data={
            'username': 'test.login@example.com',
            'password': 'password'
        }, follow=True)

        self.assertRedirects(response, '/')

    def test_logout(self):
        """Test logout resource."""
        client = Client()
        response = client.get('/logout')
        self.assertRedirects(response, '/login')

    def test_register_form(self):
        """Test register form rendering."""
        client = Client()
        response = client.get('/register')
        self.assertEqual(response.status_code, 200)