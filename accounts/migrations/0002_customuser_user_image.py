# Generated by Django 4.0.1 on 2022-02-19 09:33

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='user_image',
            field=models.ImageField(default=1, upload_to=accounts.models.upload_pic_image_path),
            preserve_default=False,
        ),
    ]