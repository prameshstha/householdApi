import os

from django.db import models

# Create your models here.
from accounts.models import CustomUser
from datetime import datetime


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_pic_image_path(instance, filename):
    print(instance, 'group')
    new_filename = datetime.now()
    name, ext = get_filename_ext(filename)
    name = name[:5]
    final_filename = '{name}-{new_filename}{ext}'.format(new_filename=new_filename, ext=ext, name=name)
    print(new_filename, final_filename, name, ext, filename, instance)
    return 'groups/' + str(instance) + '/pic/{final_filename}'.format(
        new_filename=new_filename,
        final_filename=final_filename
    )


class Groups(models.Model):
    group_admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='group_admin')
    group_pic = models.ImageField(upload_to=upload_pic_image_path, blank=True, null=True, )
    group_name = models.CharField(max_length=255)
    group_details = models.CharField(max_length=255, null=True, blank=True)
    group_country = models.CharField(max_length=255, blank=True, null=True)
    group_members = models.ManyToManyField(CustomUser, related_name='member_of_group', blank=True)
    group_created_at = models.DateTimeField(auto_now_add=True)
    group_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('group_admin', 'group_name',)

    def __str__(self):
        return str(self.group_name)


class Friends(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_id')
    friend_id = models.ManyToManyField(CustomUser, related_name='friend_id')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user_id)
