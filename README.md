# 智能自动数据获取分析系统Django后端开发日记
## 数据库设计

话题讨论（TopicComment）

|属性|类型|备注|
|:----:|:----:|:----:|
|tc_id|AutoField|编号id，自增主键|
|tc_tag|CharField(100)|话题标签|
|tc_user_id|CharField(200)|发布此微博用户id|
|tc_screen_name|CharField(500)|发布此微博用户名|
|tc_weibo_id|CharField(200)|当前微博id|
|tc_text|TextField|微博正文|
|tc_location|CharField(200)|微博位置|
|tc_created_at|DateField|发布时间|
|tc_source|CharField(200)|发布来源|
|tc_attitudes_count|IntegerField|点赞数|
|tc_comments_count|IntegerField|评论数|
|tc_reposts_count|IntegerField|转发数|
|tc_topics|CharField(1000)|所属主题|
|tc_at_users|CharField(1000)|@用户|

汽车之家口碑（AutohomeData）

|属性|类型|备注|
|:----:|:----:|:----:|
|auto_id|AutoField|编号id|
|auto_brand|CharField|品牌|
|auto_series|CharField|车系|
|auto_category|CharField|类别|
|auto_tag|CharField|标签|
|auto_evaluate|CharField|正负面评估|
|auto_text|CharField|内容|

## 逻辑设计

* 首页显示宝马，奔驰，奥迪三类车型的微博词云
* 在文字旁边，点击链接将进入单个类别显示，展示每个类别下，显示微博的频数直方图？还有情感分析的图表统计，以及汽车之家的口碑分类别展示