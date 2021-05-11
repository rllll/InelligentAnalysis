from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
import crawler.WeiboAuto
from crawler.models import TopicComment,AutohomeData
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

def deleteautohome(request):
    """
    删除汽车之家所有数据
    """
    q = AutohomeData.objects.all().delete()
    return HttpResponse("successfully!")

def autohomedata(request):
    """
    将汽车之家数据存入数据库
    """
    cwd = os.getcwd()+'/data/'
    for brand in os.listdir(cwd):
        cur_path = cwd+brand+'/'
        for txt in os.listdir(cur_path):
            f = open(cur_path+txt,'r',encoding='utf-8')
            for line in f.readlines():
                line = line.strip('\n')
                s_list = line.split(';')
                if len(s_list) < 5:
                    continue
                q = AutohomeData()
                q.auto_brand = brand
                q.auto_series = s_list[0]
                q.auto_category = s_list[1]
                q.auto_tag = s_list[2]
                q.auto_evaluate = s_list[3]
                q.auto_text = s_list[4]
                print('[正在存储...]'+brand+"("+s_list[0]+")"+"("+s_list[1]+")")
                q.save()
    return HttpResponse('successfully!')

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
    """
    获取出现次数最多的前20的词汇
    """
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
    """
    获取数据
    """
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
    """
    获取三种车系的词云数据，总体页面
    """
    if request.method == 'POST':
        q_list = ['#宝马','#奔驰','#奥迪']
        all_data = {}
        for q in q_list:
            res = get_data(q)
            all_data[q[1:]] = res
        return JsonResponse(all_data)
    else:
        return render(request,'echarts.html',csrf(request))

def singleshow(request,tag):
    """
    根据不同的车系，展示不同的数据页面
    """
    mycsrf = csrf(request)
    context = {}
    context['tag'] = tag
    context['csrf_token'] = mycsrf['csrf_token']
    return render(request,'singleshow.html',context)

def feelingdata(tag):
    """
    利用snownlp分析词汇的正负面，返回积极词汇和消极词汇
    """
    response = {
        'success':1,
        'pos_data':[],
        'neg_data':[]
    }
    try:
        query_set = TopicComment.objects.filter(tc_tag=tag)
        text_list = []
        for q in query_set:
            cur_list = jieba.lcut(q.tc_text)
            text_list += cur_list
        cwd = os.getcwd()+'/crawler/'
        stp_words_set = {line.strip() for line in open(cwd + 'cn_stopwords.txt',encoding='utf-8')}
        positive_list = []
        negative_list = []
        for text in text_list:
            text_strip = text.strip()
            if text_strip in stp_words_set:
                continue
            if len(text_strip) == 0:
                continue
            each_word = snownlp.SnowNLP(text)
            feeling = each_word.sentiments
            if feeling >= 0.9:
                positive_list.append(text_strip)
            elif feeling < 0.1:
                negative_list.append(text_strip)
        positive_count = {}
        for t in positive_list:
            positive_count[t] = positive_count.get(t,0)+1
        positive_data_list = sorted(positive_count.items(), key= lambda x : x[1], reverse=True)
        for x in positive_data_list[0:20]:
            item = {}
            item['name'] = x[0]
            item['value'] = x[1]
            response['pos_data'].append(item)
        negative_count = {}
        for t in negative_list:
            negative_count[t] = negative_count.get(t,0)+1
        negative_data_list = sorted(negative_count.items(), key= lambda x : x[1], reverse=True)
        for x in negative_data_list[0:20]:
            item = {}
            item['name'] = x[0]
            item['value'] = x[1]
            response['neg_data'].append(item)
    except Exception as e:
        response['success'] = 0
        response['error_msg'] = e
    return response

def showgetdata(request):
    """
    根据不同的tag（宝马，奥迪，奔驰）获取相应的数据
    item1代表所有词汇，用于词云展示
    item2区别了词汇情感正负面，用于展示
    """
    if request.method == 'POST':
        tag = request.POST['tag']
        all_response = {}
        res_weibo = get_data(tag)
        data = []
        all_response['item1'] = {}
        if res_weibo['success'] == 1:
            for item in res_weibo['data']:
                cur = []
                cur.append(item['name'])
                cur.append(item['value'])
                data.append(cur)
            data = data[0:20]
            all_response['item1']['success'] = 1
            all_response['item1']['data'] = data
        else:
            all_response['item1']['success'] = 0
        feel_data = feelingdata(tag)
        all_response['item2'] = {}
        if feel_data['success'] == 1:
            all_response['item2']['success'] = 1
            all_response['item2']['pos_data'] = feel_data['pos_data']
            all_response['item2']['neg_data'] = feel_data['neg_data']
        else:
            all_response['item2']['success'] = 0
        return JsonResponse(all_response)
    else:
        return {'error':'it is not a POST request!'}

def autohomeapi(request):
    """
    汽车之家的数据获取内容
    """
    if request.method == 'POST':
        autohome_data = {}
        brand = request.POST['brand']
        brand = brand[1:]
        autohome_data['brand'] = brand
        try:
            q_set = AutohomeData.objects.filter(auto_brand=brand)
            series_map = {}
            dataset = []
            dataset.append(['车系'])
            xAix = ['空间','动力','操控','油耗','舒适性','外观','内饰','性价比']
            for x in xAix:
                cur_l = []
                cur_l.append(x)
                dataset.append(cur_l)
            total_emotion = []
            neg_part_data = []
            pos_part_data = []
            for q in q_set:
                if q.auto_series not in dataset[0]:
                    dataset[0].append(q.auto_series)
                    e_list = []
                    t0 = AutohomeData.objects.filter(auto_series=q.auto_series,auto_evaluate='0')
                    it0 = {}
                    it0['name'] = '负面评价'
                    it0['value'] = len(t0)
                    e_list.append(it0)

                    part = []
                    k_v = {}
                    for m in t0:
                        k_v[m.auto_tag] = k_v.get(m.auto_tag,0) + 1
                    for k in k_v.keys():
                        xxx = {}
                        xxx['name'] = k
                        xxx['value'] = k_v[k]
                        part.append(xxx)
                    neg_part_data.append(part)

                    t1 = AutohomeData.objects.filter(auto_series=q.auto_series,auto_evaluate='1')
                    it1 = {}
                    it1['name'] = '正面评价'
                    it1['value'] = len(t1)
                    e_list.append(it1)

                    part = []
                    k_v = {}
                    for m in t1:
                        k_v[m.auto_tag] = k_v.get(m.auto_tag,0) + 1
                    for k in k_v.keys():
                        xxx = {}
                        xxx['name'] = k
                        xxx['value'] = k_v[k]
                        part.append(xxx)
                    pos_part_data.append(part)

                    total_emotion.append(e_list)

                    for i in range(len(xAix)):
                        cur_query = AutohomeData.objects.filter(auto_series=q.auto_series,auto_category=xAix[i])
                        size = len(cur_query)
                        dataset[i+1].append(size)

                series_map[q.auto_series] = series_map.get(q.auto_series,0) + 1
            series_list = []
            for key in series_map.keys():
                item = {}
                item['name'] = key
                item['value'] = series_map[key]
                series_list.append(item)
        except Exception as e:
            print(e)
        # 该展示哪些数据呢？
        autohome_data['series_list'] = series_list
        autohome_data['dataset'] = dataset
        autohome_data['emotions'] = total_emotion
        autohome_data['negpart'] = neg_part_data
        autohome_data['pospart'] = pos_part_data
        return JsonResponse(autohome_data)
    else:
        return {'error':'it is not a POST request!'}
