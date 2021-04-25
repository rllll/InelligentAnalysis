from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
import crawler.WeiboAuto
from crawler.models import TopicComment
from datetime import datetime
import jieba
import wordcloud
import os
import snownlp
import matplotlib.pyplot as plt

from django.http import JsonResponse
from django.template.context_processors import csrf

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

def show(request):
    try:
        query_set = TopicComment.objects.filter(tc_tag="#宝马")
        text_list = []
        for q in query_set:
            cur_list = jieba.lcut(q.tc_text)
            text_list += cur_list
        positive_list = []
        negative_list = []
        for text in text_list:
            each_word = snownlp.SnowNLP(text)
            feeling = each_word.sentiments
            if feeling >= 0.9:
                positive_list.append(text)
            elif feeling < 0.1:
                negative_list.append(text)
        positive_str = " ".join(positive_list)
        negative_str = " ".join(negative_list)
        text_str = " ".join(text_list)
        cwd = os.getcwd()+'/crawler/'
        stp_words_set = {line.strip() for line in open(cwd + 'cn_stopwords.txt',encoding='utf-8')}
        w = wordcloud.WordCloud(width=1000,
                                height=700,
                                background_color='white',
                                font_path='simhei.ttf',
                                stopwords=stp_words_set)
        w_p = wordcloud.WordCloud(width=1000,
                                height=700,
                                font_path="simhei.ttf",
                                background_color='white',
                                stopwords=stp_words_set)
        w_n = wordcloud.WordCloud(width=1000,
                                height=700,
                                font_path="simhei.ttf",
                                background_color='white',
                                stopwords=stp_words_set)
        w.generate(text_str)
        
        w_p.generate(positive_str)
        w_n.generate(negative_str)
        w.to_file(cwd + 'BMW.png')
        w_p.to_file(cwd+'positive.png')
        w_n.to_file(cwd+'negative.png')

        pos_count = len(positive_list)
        neg_count = len(negative_list)
        labels = ['Positive Side', 'Negative Side']
        fracs = [pos_count,neg_count]
        explode = [0.1,0] # 0.1 凸出这部分，
        plt.axes(aspect=1)
        plt.pie(x=fracs, labels=labels, explode=explode,autopct='%3.1f %%',
             shadow=True,labeldistance=1.1, startangle = 90,pctdistance = 0.6)
        plt.savefig(cwd+"emotions_pie_chart.jpg",dpi = 360)
    except Exception as e:
        print(e)
    return HttpResponse('this is a show page')


def toptopic(request):
    try:
        query_set = TopicComment.objects.all()
        topic_list = []
        for q in query_set:
            cur = q.tc_topics.split(',')
            topic_list += cur
        hash_count = {}
        for topic in topic_list:
            if topic in hash_count.keys():
                hash_count[topic] += 1
            else:
                hash_count[topic] = 1
        count_list = sorted(hash_count.items(), key = lambda x: x[1], reverse = True)
        print(count_list[0:10])
    except Exception as e:
        print(e)
    return HttpResponse("this is top 10 topic")

def get_data(tag):
    response = {
        'success':1,
        'data':[]
    }
    try:
        query_set = TopicComment.objects.filter(tc_tag=tag)
        text_list = []
        for q in query_set:
            cur_list = jieba.lcut(q.tc_text)
            text_list += cur_list
        cwd = os.getcwd()+'/crawler/'
        stp_words_set = {line.strip() for line in open(cwd + 'cn_stopwords.txt',encoding='utf-8')}
        cur_data = {}
        for text in text_list:
            text_strip = text.strip()
            if text_strip in stp_words_set:
                continue
            if len(text_strip) == 0:
                continue
            if text_strip in cur_data.keys():
                cur_data[text_strip] += 1
            else:
                cur_data[text_strip] = 1
        data_list = sorted(cur_data.items(), key= lambda x : x[1], reverse=True)
        for x in data_list[0:200]:
            item = {}
            item['name'] = x[0]
            item['value'] = x[1]
            response['data'].append(item)
    except Exception as e:
        response['success'] = 0
        response['error_msg'] = e
    return response
        

def echarts(request):
    if request.method == 'POST':
        q_list = ['#宝马','#奔驰','#奥迪']
        all_data = {}
        for q in q_list:
            res = get_data(q)
            all_data[q[1:]] = res
        return JsonResponse(all_data)
    else:
        return render(request,'echarts.html',csrf(request))