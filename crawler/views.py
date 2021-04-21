from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
import crawler.WeiboAuto
from crawler.models import TopicComment
from datetime import datetime

# Create your views here.
def index(request):
    return render(request,'index.html')

def startcrawler(request):
    topic_tag = request.POST['topic_tag']
    wb = crawler.WeiboAuto.WeiboAuto()
    wb.start(topic_tag)
    weibos = wb.get_weibos()
    for w in weibos:
        try:
            q = TopicComment.objects.get(tc_weibo_id=w['id'])
        except TopicComment.DoesNotExist:
            q = TopicComment()
            q.tc_tag = topic_tag
            q.tc_user_id = w['user_id']
            q.tc_screen_name = w['screen_name']
            q.tc_weibo_id = w['id']
            q.tc_text = w['text']
            q.tc_location = w['location']
            q.tc_created_at = datetime.strptime(w['created_at'],"%Y-%m-%d")
            q.tc_source = w['source']
            q.tc_attitudes_count = w['attitudes_count']
            q.tc_comments_count = w['comments_count']
            q.tc_reposts_count = w['reposts_count']
            q.tc_topics = w['topics']
            q.tc_at_users = w.get('at_users','')
            q.save()
    context = {
        'topic_tag':topic_tag
    }
    return render(request,'show.html',context)