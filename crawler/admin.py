from django.contrib import admin

from .models import TopicComment,AutohomeData

# Register your models here.
admin.site.register(TopicComment)

admin.site.register(AutohomeData)