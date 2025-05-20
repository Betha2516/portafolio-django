from django.contrib import admin
from .models import Comment, Client, Project
# Register your models here.
admin.site.register(Client)
admin.site.register(Comment)
admin.site.register(Project)
