# Generated by Django 4.0.1 on 2022-02-19 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0002_delete_grouptype_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='groups',
            name='group_details',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]