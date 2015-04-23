from django.contrib import admin
from core.models import Member, Queue, Task
from guardian.admin import GuardedModelAdmin


class MemberAdmin(GuardedModelAdmin):
    pass


class QueueAdmin(GuardedModelAdmin):
    pass


admin.site.register(Member, MemberAdmin)
admin.site.register(Queue, QueueAdmin)
admin.site.register(Task)