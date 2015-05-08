"""Unit tests for the API"""
import unittest

from rest_framework.test import APIClient
from core.models import Member, Group


class ApiTest(unittest.TestCase):

    """API tests"""

    def setUp(self):
        """Create two users, a group and a taskmaster"""
        self.client = APIClient()
        self.group = Group.objects.create(name='First Group')
        self.member = Member.objects.create_user(email='api.tester@example.com',
                                                 password='apitester',
                                                 name='Api Tester',
                                                 group=self.group)
        self.member_two = Member.objects.create_user(email='api.tester2@example.com',
                                                     password='apitester2',
                                                     name='Api Tester Two',
                                                     group=self.group)
        self.taskmaster = Member.objects.create_user(email='api.taskmaster@example.com',
                                                     password='taskmaster',
                                                     name='Taskmaster',
                                                     group=self.group)
        self.group.taskmasters.add(self.taskmaster)

    def test_user_info(self):
        """Test if we can get the same user info from two different resources."""
        self.client.login(email='api.tester@example.com', password='apitester')
        content = self.client.get('/api/users/{}'.format(self.member.id)).content

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

    def test_group_info(self):
        """Test if we can get info about the group"""
        self.client.login(email='api.tester@example.com', password='apitester')
        data = self.client.get('/api/groups/{}'.format(self.group.id))

        self.assertEqual(data['name'], self.group.name)
        self.assertListEqual(data['members'], [self.member.id, self.member_two.id])

        self.client.logout()

    def test_create_task(self):
        """Test if we can correctly create a task that sits idly in a group."""
        self.client.login(email='api.tester@example.com', password='apitester')
        task = {
            'title': 'API task',
            'text': 'API task',
            'group': self.group.id
        }

        content = self.client.post('/api/tasks', task).content

        self.assertTrue('id' in content)

        api_task = self.client.get('/api/tasks/{}'.format(content['id']))

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

        task_id = self.client.post('/api/tasks', task).content['id']
        self.client.put('/api/tasks/{}/assign-to'.format(task_id), {'memberId': self.member.id})

        api_member = self.client.get('/api/users/{}'.format(self.member.id)).content
        self.assertEqual(api_member['currentTaskId'], task_id)

        self.client.put('/api/tasks/{}/done'.format(task_id))
        api_task = self.client.get('/api/tasks/{}'.format(task_id)).content
        api_member = self.client.get('/api/users/{}'.format(self.member.id)).content
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
        task_id = response.content['id']
        self.assertEqual(response.status_code, 200)

        # Assign the task to a user
        response = self.client.post(
            '/api/tasks/{}/assign-to'.format(task_id),
            {'memberId': self.member.id}
        )
        self.assertEqual(response.status_code, 200)

        # Check if the task's and the user's group are the same
        api_task = self.client.get('/api/tasks/{}'.format(task_id)).content
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
        task_id = response.content['id']
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
        task_id = self.client.post('/api/tasks', task).content['id']
        task_id_two = self.client.post('/api/tasks', task_two)

        self.client.put('/api/tasks/{}/assign-to'.format(task_id), {'memberId': self.member.id})
        self.client.put('/api/tasks/{}/assign-to'.format(task_id_two), {'memberId': self.member.id})

        response = self.client.put('/api/users/{}/work-on-next'.format(self.member.id))
        self.assertEqual(response.status_code, 200)

        content = self.client.get('/api/users/{}'.format(self.member.id)).content
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
        task_id = self.client.post('/api/tasks', task).content['id']

        response = self.client.delete('/api/tasks/{}'.format(task_id))
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.client.login(email='api.taskmaster@example.com', password='taskmaster')

        response = self.client.delete('/api/tasks/{}'.format(task_id))
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/api/tasks/123456789')
        self.assertEqual(response.status_code, 404)

        self.client.logout()
