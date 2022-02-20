from django.contrib import admin

# Register your models here.
from group.models import Friends, Groups

admin.site.register(Friends)
admin.site.register(Groups)