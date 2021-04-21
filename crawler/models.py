from django.db import models

# 账号：root
# 密码：SHUces_lwy

# Create your models here.
class TopicComment(models.Model):
    tc_id = models.AutoField(primary_key=True,verbose_name="编号id，自增主键")
    tc_tag = models.CharField(max_length=100,verbose_name="话题标签")
    tc_user_id = models.CharField(max_length=200,null=True,blank=True,verbose_name="发布此微博用户id")
    tc_screen_name = models.CharField(max_length=500,null=True,blank=True,verbose_name="发布此微博用户名")
    tc_weibo_id = models.CharField(max_length=200,null=True,blank=True,verbose_name="当前微博id")
    tc_text = models.TextField(verbose_name="微博正文",null=True,blank=True)
    tc_location = models.CharField(max_length=200,null=True,blank=True,verbose_name="微博位置")
    tc_created_at = models.DateField(null=True,blank=True,verbose_name="发布时间")
    tc_source = models.CharField(max_length=200,null=True,blank=True,verbose_name="发布来源")
    tc_attitudes_count = models.IntegerField(null=True,blank=True,verbose_name="点赞数")
    tc_comments_count = models.IntegerField(null=True,blank=True,verbose_name="评论数")
    tc_reposts_count = models.IntegerField(null=True,blank=True,verbose_name="转发数")
    tc_topics = models.CharField(max_length=1000,null=True,blank=True,verbose_name="所属主题")
    tc_at_users = models.CharField(max_length=1000,null=True,blank=True,verbose_name="@用户")
    def __str__(self):
        return self.tc_screen_name + "( " + self.tc_weibo_id + " )"
    class Meta:
        verbose_name="话题评论"
        verbose_name_plural="话题评论"