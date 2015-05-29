"""Unit tests for the API"""
import unittest

from api import utils
from core.models import Member, Group
from rest_framework.test import APIClient
from django.http import JsonResponse


class UtilsTest(unittest.TestCase):

    """Tests of utils.py"""

    def test_json_decode(self):
        """Test if data from JsonResponses is extracted correctly."""
        d = {
            'some': 'test',
            'data': True,
            'derp': 12345
        }

        response = JsonResponse(data=d)

        decoded_data = utils.response_to_json(response)

        self.assertEqual(d, decoded_data)


class GroupApiTest(unittest.TestCase):

    """API tests for the groups API."""

    def setUp(self):
        """Create two users, a group and a taskmaster"""
        self.client = APIClient()
        self.group = Group.objects.create(name='First Group')
        self.member = Member.objects.create_user(
            email='api.tester@example.com',
            password='apitester',
            name='Api Tester',
            group=self.group
        )
        self.member_two = Member.objects.create_user(
            email='api.tester2@example.com',
            password='apitester2',
            name='Api Tester Two',
            group=self.group
        )
        self.taskmaster = Member.objects.create_user(
            email='api.taskmaster@example.com',
            password='taskmaster',
            name='Taskmaster',
            group=self.group
        )
        self.group.taskmasters.add(self.taskmaster)

    def tearDown(self):
        self.taskmaster.delete()
        self.member.delete()
        self.member_two.delete()
        self.group.delete()

    def test_group_info(self):
        """Test if we can get info about the group."""
        self.client.login(email='api.tester@example.com', password='apitester')
        data = utils.response_to_json(self.client.get('/api/groups/{}'.format(self.group.id)))

        self.assertEqual(data['name'], self.group.name)
        self.assertEqual(set(data['members']), {self.member.id, self.member_two.id, self.taskmaster.id})

        self.client.logout()

    def test_create_group(self):
        """Test if a user can create a group."""
        self.client.login(email='api.tester@example.com', password='apitester')
        response = self.client.post('/api/groups', data={
            'name': 'API created group'
        }, format='json')

        self.assertEqual(response.status_code, 201)

        data = utils.response_to_json(response)
        group = utils.response_to_json(self.client.get('/api/groups/{}'.format(data['id'])))

        self.assertEqual(data, group)

        self.assertEqual(group['taskmasters'], [self.member.id])

    def test_create_many_groups(self):
        """Test if a user can create more groups than allowed."""
        self.client.login(email='api.tester@example.com', password='apitester')
        for i in range(10):
            self.client.post('/api/groups', data={
                'name': 'API created group #{}'.format(i)
            })

        response = self.client.post('/api/groups', data={
            'name': 'API created group #{}'.format(i)
        })

        self.assertEqual(response.status_code, 403)


class UserApiTest(unittest.TestCase):

    """API tests for the user API."""

    def setUp(self):
        """Create two users, a group and a taskmaster"""
        self.client = APIClient()
        self.group = Group.objects.create(name='First Group')
        self.member = Member.objects.create_user(
            email='api.tester@example.com',
            password='apitester',
            name='Api Tester',
            group=self.group
        )

    def tearDown(self):
        self.member.delete()
        self.group.delete()

    def test_user_info(self):
        """Test if we can get the same user info from two different resources."""
        self.client.login(email='api.tester@example.com', password='apitester')
        content = utils.response_to_json(self.client.get('/api/users/{}'.format(self.member.id)))

        self.assertEqual(content['email'], self.member.email)
        self.assertEqual(content['name'], self.member.name)
        self.assertListEqual(content['groups'], [self.group.id])

        self.assertEqual(content['tasks'], [])
        self.assertEqual(content['currentTaskId'], None)

        # Test alternate route
        content = self.client.get('/api/me')

        self.assertEqual(content['email'], self.member.email)
        self.assertEqual(content['name'], self.member.name)
        self.assertListEqual(content['groups'], [self.group.id])

        # Test non existent user
        response = self.client.get('/api/users/{}'.format(self.member.id))
        self.assertEqual(response.status_code, 404)

        self.client.logout()


class TaskApiTest(unittest.TestCase):

    """API tests for the task API."""

    def setUp(self):
        """Create two users, a group and a taskmaster"""
        self.client = APIClient()
        self.group = Group.objects.create(name='First Group')
        self.member = Member.objects.create_user(
            email='api.tester@example.com',
            password='apitester',
            name='Api Tester',
            group=self.group
        )
        self.member_two = Member.objects.create_user(
            email='api.tester2@example.com',
            password='apitester2',
            name='Api Tester Two',
            group=self.group
        )
        self.taskmaster = Member.objects.create_user(
            email='api.taskmaster@example.com',
            password='taskmaster',
            name='Taskmaster',
            group=self.group
        )
        self.group.taskmasters.add(self.taskmaster)

    def tearDown(self):
        self.taskmaster.delete()
        self.member.delete()
        self.member_two.delete()
        self.group.delete()

    def test_create_task(self):
        """Test if we can correctly create a task that sits idly in a group."""
        self.client.login(email='api.tester@example.com', password='apitester')
        task = {
            'title': 'API task',
            'text': 'API task',
            'group': self.group.id
        }

        content = utils.response_to_json(self.client.post('/api/tasks', task))

        self.assertTrue('id' in content)

        api_task = utils.response_to_json(self.client.get('/api/tasks/{}'.format(content['id'])))

        self.assertEqual(api_task['title'], task['title'])
        self.assertEqual(api_task['text'], task['text'])
        self.assertEqual(api_task['group'], task['group'])
        self.assertEqual(api_task['member'], None)
        self.assertFalse(api_task['done'])

        self.client.logout()

    def test_finish_task(self):
        """Test if tasks that are currently being worked on can be finished."""
        self.client.login(email='api.tester@example.com', password='apitester')
        task = {
            'title': 'API task',
            'text': 'API task',
            'group': self.group.id
        }

        task_id = utils.response_to_json(self.client.post('/api/tasks', task))['id']
        self.client.put('/api/tasks/{}/assign-to'.format(task_id), {'memberId': self.member.id})

        api_member = utils.response_to_json(self.client.get('/api/users/{}'.format(self.member.id)))
        self.assertEqual(api_member['currentTaskId'], task_id)

        self.client.put('/api/tasks/{}/done'.format(task_id))
        api_task = utils.response_to_json(self.client.get('/api/tasks/{}'.format(task_id)))
        api_member = utils.response_to_json(self.client.get('/api/users/{}'.format(self.member.id)))
        self.assertTrue(api_task['done'])
        self.assertIsNone(api_member['currentTaskId'])

        self.client.logout()

    def test_assign_task(self):
        """Test if tasks can be assigned to one's own queue and by the taskmaster to any queue."""
        self.client.login(email='api.tester@example.com', password='apitester')
        task = {
            'title': 'API task',
            'text': 'API task',
            'group': self.group.id
        }

        # Create a new task
        response = self.client.post('/api/tasks', task)
        task_id = utils.response_to_json(response)['id']
        self.assertEqual(response.status_code, 200)

        # Assign the task to a user
        response = self.client.post(
            '/api/tasks/{}/assign-to'.format(task_id),
            {'memberId': self.member.id}
        )
        self.assertEqual(response.status_code, 200)

        # Check if the task's and the user's group are the same
        api_task = utils.response_to_json(self.client.get('/api/tasks/{}'.format(task_id)))
        self.assertEqual(api_task['groupId'], self.group.id)

        # Check if we can reassign a task (or rather not)
        response = self.client.put(
            '/api/tasks/{}/assign-to'.format(task_id),
            {'memberId': self.member_two.id}
        )
        self.assertEqual(response.status_code, 400)

        # Check if we can assign tasks to other users without being taskmaster
        task = {
            'title': 'API task 2',
            'text': 'API task 2',
            'group': self.group.id
        }

        response = self.client.post('/api/tasks', task)
        task_id = utils.response_to_json(response)['id']
        self.assertEqual(response.status_code, 200)

        # Assign the task to another user
        response = self.client.post(
            '/api/tasks/{}/assign-to'.format(task_id),
            {'memberId': self.member_two.id}
        )
        self.assertEqual(response.status_code, 403)

        # Test if the taskmaster can assign tasks to anybody
        self.client.logout()
        self.client.login(email='api.taskmaster@example.com', password='taskmaster')

        response = self.client.post(
            '/api/tasks/{}/assign-to'.format(task_id),
            {'memberId': self.member_two.id}
        )
        self.assertEqual(response.status_code, 200)

        self.client.logout()

    def test_work_on_next_task(self):
        """Test if the 'work on next task' functionality works."""
        self.client.login(email='api.tester@example.com', password='apitester')
        task = {
            'title': 'API task',
            'text': 'Work on me',
            'group': self.group.id
        }
        task_two = {
            'title': 'API task 2',
            'text': 'Work on me 2',
            'group': self.group.id
        }

        # Test response if there's no task in the queue
        response = self.client.put('/api/users/{}/work-on-next'.format(self.member.id))
        self.assertEqual(response.status_code, 400)

        # Add two tasks to the user's queue
        task_id = utils.response_to_json(self.client.post('/api/tasks', task))['id']
        task_id_two = self.client.post('/api/tasks', task_two)

        self.client.put('/api/tasks/{}/assign-to'.format(task_id), {'memberId': self.member.id})
        self.client.put('/api/tasks/{}/assign-to'.format(task_id_two), {'memberId': self.member.id})

        response = self.client.put('/api/users/{}/work-on-next'.format(self.member.id))
        self.assertEqual(response.status_code, 200)

        content = utils.response_to_json(self.client.get('/api/users/{}'.format(self.member.id)))
        self.assertEqual(content['currentTaskId'], task_id)

        # Check if only the user can set a task as in progress
        self.client.logout()
        self.client.login(email='api.taskmaster@example.com', password='taskmaster')

        response = self.client.put('/api/users/{}/work-on-next'.format(self.member.id))
        self.assertEqual(response.status_code, 403)

        self.client.logout()

    def test_delete_task(self):
        """Only taskmasters should be able any delete task."""
        self.client.login(email='api.tester@example.com', password='apitester')

        task = {
            'title': 'API task',
            'text': 'Work on me',
            'group': self.group.id
        }
        task_id = utils.response_to_json(self.client.post('/api/tasks', task))['id']

        response = self.client.delete('/api/tasks/{}'.format(task_id))
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.client.login(email='api.taskmaster@example.com', password='taskmaster')

        response = self.client.delete('/api/tasks/{}'.format(task_id))
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/api/tasks/123456789')
        self.assertEqual(response.status_code, 404)

        self.client.logout()