# Generated by Django 3.1.6 on 2021-04-21 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='topiccomment',
            name='tc_tag',
            field=models.CharField(default=0, max_length=100, verbose_name='话题标签'),
            preserve_default=False,
        ),
    ]
