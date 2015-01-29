from django.contrib.auth.models import User
from django.db import models
from taskstack import settings


class Member(models.Model):
    """ A member as described in README.md """
    user = models.OneToOneField(User)
    current_task = models.OneToOneField('Task', null=True, blank=True)

    def __str__(self):
        return self.user.username


class Queue(models.Model):
    """ A Queue as described in README.md """
    user = models.OneToOneField(User)
    limit = models.IntegerField(default=settings.DEFAULT_QUEUE_SIZE)
    objects = QueueManager()

    def is_full(self):
        return self.task_set.count() >= self.limit

    def __str__(self):
        return "{user}'s queue".format(user=self.user.username)


class QueueManager(models.Manager):
    """
    We need to make sure that a queue can never go over its task limit.
    Maybe use a custom manager? Not sure yet. We also need to set `added_to_queue`
    on the task somehow.
    """
    pass


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