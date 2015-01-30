from django.contrib.auth.models import User
from django.db import models
from taskstack import settings
from .exceptions import QueueFullException


class Group(models.Model):
    """A group as descriped in README.md."""
    name = models.TextField()


class Member(models.Model):
    """
    A member as described in README.md.
    Members can be without a group.
    """
    user = models.OneToOneField(User)
    group = models.ForeignKey(Group, null=True, blank=True)
    current_task = models.OneToOneField('Task', null=True, blank=True)

    def __init__(self, user=None, group=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.group = group

    def __str__(self):
        return self.user.username


class Queue(models.Model):
    """A Queue as described in README.md."""
    user = models.OneToOneField(User)
    limit = models.IntegerField(default=settings.DEFAULT_QUEUE_SIZE)

    def add_task(self, task):
        """
        Adds a task to the queue and respects its task limit.
        You must always use this method instead of task_set.add.
        If you read this and have a better idea that enables us to use add, go ahead.
        """
        if self.is_full():
            raise QueueFullException("You cannot add more than {} tasks to this queue".format(self.limit))
        else:
            self.task_set.add(task)

    def is_full(self):
        """Return whether the queue has reached its maximum number of tasks."""
        return self.task_set.count() >= self.limit

    def __str__(self):
        return "{}'s queue".format(self.user.username)


class Task(models.Model):
    """
    A task as described in README.md
    Pretty much self explanatory except for `added_to_queue`. I'm not sure yet
    whether to use a date here or some other method of keeping tasks in order.
    (the order they were added to a queue)
    """
    queue = models.ForeignKey(Queue)
    title = models.TextField()
    text = models.TextField()
    created = models.DateTimeField(auto_now=True)
    added_to_queue = models.DateTimeField()

    def __str__(self):
        return self.title
