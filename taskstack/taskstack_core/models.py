from django.contrib.auth.models import User
from django.db import models
from taskstack import settings


class Member(models.Model):
    user = models.OneToOneField(User)
    current_task = models.OneToOneField('Task', null=True, blank=True)

    def __str__(self):
        return self.user.username


class Queue(models.Model):
    user = models.OneToOneField(User)
    limit = models.IntegerField(default=settings.DEFAULT_QUEUE_SIZE)

    def is_full(self):
        return self.task_set.count() >= self.limit

    def __str__(self):
        return "{user}'s queue".format(user=self.user.username)


class Task(models.Model):
    queue = models.ForeignKey(Queue)
    title = models.TextField()
    text = models.TextField()

    def __str__(self):
        return self.title