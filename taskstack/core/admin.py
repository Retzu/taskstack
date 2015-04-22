from django.contrib import admin
from . import models

admin.site.register(models.Member)
admin.site.register(models.Queue)
admin.site.register(models.Task)

