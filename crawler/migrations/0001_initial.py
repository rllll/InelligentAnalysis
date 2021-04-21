# Generated by Django 3.1.6 on 2021-04-21 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TopicComment',
            fields=[
                ('tc_id', models.AutoField(primary_key=True, serialize=False, verbose_name='编号id，自增主键')),
                ('tc_user_id', models.CharField(blank=True, max_length=200, null=True, verbose_name='发布此微博用户id')),
                ('tc_screen_name', models.CharField(blank=True, max_length=500, null=True, verbose_name='发布此微博用户名')),
                ('tc_weibo_id', models.CharField(blank=True, max_length=200, null=True, verbose_name='当前微博id')),
                ('tc_text', models.TextField(blank=True, null=True, verbose_name='微博正文')),
                ('tc_location', models.CharField(blank=True, max_length=200, null=True, verbose_name='微博位置')),
                ('tc_created_at', models.DateField(blank=True, null=True, verbose_name='发布时间')),
                ('tc_source', models.CharField(blank=True, max_length=200, null=True, verbose_name='发布来源')),
                ('tc_attitudes_count', models.IntegerField(blank=True, null=True, verbose_name='点赞数')),
                ('tc_comments_count', models.IntegerField(blank=True, null=True, verbose_name='评论数')),
                ('tc_reposts_count', models.IntegerField(blank=True, null=True, verbose_name='转发数')),
                ('tc_topics', models.CharField(blank=True, max_length=1000, null=True, verbose_name='所属主题')),
                ('tc_at_users', models.CharField(blank=True, max_length=1000, null=True, verbose_name='@用户')),
            ],
            options={
                'verbose_name': '话题评论',
                'verbose_name_plural': '话题评论',
            },
        ),
    ]
