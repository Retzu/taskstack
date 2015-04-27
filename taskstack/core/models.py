from django.contrib.auth.models import User
from django.db import models
from django.utils.datetime_safe import datetime
from guardian.shortcuts import assign_perm, remove_perm
from taskstack import settings
from core.exceptions import QueueFullException, UserAlreadyWorkingException


class Group(models.Model):
    """A group as described in README.md."""
    name = models.TextField()
    taskmasters = models.ManyToManyField('Member', related_name='taskmasters')

    def add_member(self, member):
        """
        Add a member to this group and also update permissions for taskmasters.
        Do *not* use Group.members.add, only this method!
        """
        self.members.add(member)
        for taskmaster in self.taskmasters.all():
            member.queue.grant_modify_permissions(taskmaster)

    def remove_member(self, member):
        """
        Remove a member from this group and update permissions for taskmasters.
        Do *not* use Group.members.remove, only this method!
        """
        self.members.remove(member)
        for taskmaster in self.taskmasters.all():
            member.queue.revoke_modify_permissions(taskmaster)

    def add_taskmaster(self, member):
        """
        Add member as a taskmaster to this group. Do so by
        adding it to the taskmaster and granting them permissions to
        the queues of every member
        """
        self.taskmasters.add(member)
        for group_member in self.members.all():
            group_member.queue.grant_modify_permissions(member)

    def remove_taskmaster(self, member):
        """
        Remove a member from taskmasters by removing them from
        the relation and revoking any permissions on the queues.
        """
        self.taskmasters.remove(member)
        for group_member in self.members.all():
            group_member.queue.revoke_modify_permissions(member)


class Member(models.Model):
    """
    A member as described in README.md.
    Members can be without a group.
    """
    user = models.OneToOneField(User, unique=True)
    name = models.TextField(null=True, blank=True)
    group = models.ForeignKey(Group, null=True, blank=True, related_name='members')
    current_task = models.OneToOneField('Task', null=True, blank=True)

    def has_perm(self, perm, obj):
        return self.user.has_perm(perm, obj)

    def work_on_next(self):
        """Tell a member to work on the next task in the queue"""
        self.current_task_done()
        # Get the oldest (=next) task
        try:
            task = self.queue.tasks.filter(done=False).order_by('-added_to_queue')[0]
            self.current_task = task
        except IndexError:
            self.current_task = None
        self.save()

    def current_task_done(self):
        """Mark the current task as done."""
        if self.current_task is not None:
            self.current_task.mark_as_done()
            self.current_task = None

    @classmethod
    def create(cls, email, password, name=None, group=None):
        """Creates a new member, an attached Django user and a queue."""
        member = cls(name=name, group=group)

        user = User.objects.create_user(username=email, email=email, password=password)
        member.user = user

        member.save()

        queue = Queue(member=member)
        queue.save()

        queue.grant_modify_permissions(member)

        member.save()

        return member

    def __str__(self):
        if self.name is not None:
            return self.name
        else:
            return self.user.email


class Queue(models.Model):
    """A Queue as described in README.md."""
    member = models.OneToOneField(Member)
    limit = models.IntegerField(default=settings.DEFAULT_QUEUE_SIZE)

    def add_task(self, task):
        """
        Adds a task to the queue and respects its task limit.
        You must always use this method instead of tasks.add.
        If you read this and have a better idea that enables us to use add, go ahead.
        """
        if self.is_full():
            raise QueueFullException('You cannot add more than {} tasks to this queue'.format(self.limit))
        else:
            self.tasks.add(task)
            task.last_queue = self
            task.added_to_queue = datetime.now()

    def remove_task(self, task):
        self.tasks.remove(task)
        task.queue = None

    def is_full(self):
        """Return whether the queue has reached its maximum number of tasks."""
        return self.tasks.count() >= self.limit

    def grant_modify_permissions(self, member):
        """
        Grant a member permissions to modify this queue. This can be
        the member who owns this queue or a taskmaster
        """
        assign_perm('add_to_queue', member.user, self)
        assign_perm('remove_from_queue', member.user, self)

    def revoke_modify_permissions(self, member):
        """
        Revoke modifying permissions from a member to this queue. Most
        likely to be used on taskmasters.
        """
        remove_perm('add_to_queue', member.user, self)
        remove_perm('remove_from_queue', member.user, self)

    def __str__(self):
        return "{}'s queue".format(self.member.user.username)

    class Meta:
        permissions = (
            ('add_to_queue', 'Add a task to queue'),
            ('remove_from_queue', 'Remove task from queue'),
        )


class Task(models.Model):
    """
    A task as described in README.md
    Pretty much self explanatory except for `added_to_queue`. I'm not sure yet
    whether to use a date here or some other method of keeping tasks in order.
    (the order they were added to a queue)
    `last_queue` keeps track of the last queue the task was in to be able to
    enforce rule #8.
    Also, tasks always have a group. Task without a Member but a group are "loose" tasks
    that lie around ready to be assigned to someone in the group.
    """
    queue = models.ForeignKey(Queue, related_name='tasks', null=True, blank=True)
    last_queue = models.ForeignKey(Queue, related_name='_last_queue_set', null=True, blank=True)
    group = models.ForeignKey(Group, related_name='tasks')
    title = models.TextField()
    text = models.TextField()
    created = models.DateTimeField(auto_now=True)
    added_to_queue = models.DateTimeField(null=True, blank=True)
    done = models.BooleanField(default=False)

    def mark_as_done(self):
        self.done = True
        self.queue = None
        self.save()

    def __str__(self):
        return '{}: {}...'.format(self.title, self.text[:20])
