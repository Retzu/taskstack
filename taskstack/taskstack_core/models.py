from django.contrib.auth.models import User
from django.db import models


class Queue(models.Model):
    user = models.OneToOneField(User)


class Task(models.Model):
    queue = models.ForeignKey(Queue)
    title = models.TextField()
    text = models.TextField()
