from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect, response
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

def autohomehtml(request):
    return render(request,'autohome.html',csrf(request))

def ahshow(request):
    return render(request,'ahshow.html',csrf(request))

def compareseries(request):
    return render(request,'compareseries.html',csrf(request))

def handleahshow(request):
    if request.method == 'POST':
        responsedata = {}
        responsedata['feelings'] = []
        responsedata['bytag'] = []
        category = ['空间','动力','操控','油耗','舒适性','外观','内饰','性价比']
        for c in category:
            item = {}
            item['name'] = c
            item['value'] = 0
            responsedata['bytag'].append(item)

        select_series = request.POST['select_series']

        try:
            q_set = AutohomeData.objects.filter(auto_series=select_series)
            pos_dict = {}
            pos_dict['name'] = '积极'
            neg_dict = {}
            neg_dict['name'] = '消极'
            for q in q_set:
                if q.auto_evaluate == '1':
                    pos_dict['value'] = pos_dict.get('value',0) + 1
                elif q.auto_evaluate == '0':
                    neg_dict['value'] = neg_dict.get('value',0) + 1
                for i in range(len(category)):
                    if q.auto_category == category[i]:
                        responsedata['bytag'][i]['value'] += 1
                        break
            responsedata['feelings'].append(pos_dict)
            responsedata['feelings'].append(neg_dict)
        except Exception as e:
            print(e)
        return JsonResponse(responsedata)

def handlecategory(request):
    if request.method == "POST":
        responsedata = {}
        responsedata['rescategory'] = []
        responsedata['resfeelings'] = []
        select_series = request.POST['select_series']
        select_category = request.POST['select_category']
        try:
            q_set = AutohomeData.objects.filter(auto_series=select_series,auto_category=select_category)
            tags = {}
            feel = {}
            for q in q_set:
                tags[q.auto_tag] = tags.get(q.auto_tag,0) + 1
                if q.auto_evaluate == '1':
                    feel['pos'] = feel.get('pos',0) + 1
                elif q.auto_evaluate == '0':
                    feel['neg'] = feel.get('neg',0) + 1
            for t in tags:
                item = {}
                item['name'] = t
                item['value'] = tags.get(t,0)
                responsedata['rescategory'].append(item)
            for f in feel:
                item = {}
                if f == 'pos':
                    item['name'] = '积极'
                else:
                    item['name'] = '消极'
                item['value'] = feel.get(f,0)
                responsedata['resfeelings'].append(item)
        except Exception as e:
            print(e)
        return JsonResponse(responsedata)

def getSeriesByBrand(brand):
    leg = []
    try:
        q_set = AutohomeData.objects.filter(auto_brand=brand)
        for q in q_set:
            ser = q.auto_series
            if ser in leg:
                continue
            leg.append(ser)
    except Exception as e:
        print(e)
    return leg

def getlegend(request):
    if request.method == 'POST':
        brand = request.POST['curbrand']
        leg = getSeriesByBrand(brand)
        resdata = {'leg':leg}
        return JsonResponse(resdata)

def getallbrands():
    allbrands = []
    q_set = AutohomeData.objects.all()
    for q in q_set:
        if q.auto_brand in allbrands:
            continue
        allbrands.append(q.auto_brand)
    return allbrands

def compareto(request):
    if request.method == "POST":
        responsedata = {}
        allbrands = ['宝马','奥迪','奔驰','特斯拉','大众','蔚来','小鹏汽车']
        brand = request.POST['curbrand']
        responsedata['all'] = []
        for b in allbrands:
            if b != brand:
                item = {}
                item['brand'] = b
                leg = getSeriesByBrand(b)
                item['leg'] = leg
                responsedata['all'].append(item)
        return JsonResponse(responsedata)

def comparegetfeelingsdatabyseries(series):
    resdata = []
    try:
        q_set = AutohomeData.objects.filter(auto_series=series)
        datajson = {}
        for q in q_set:
            if q.auto_evaluate == '1':
                datajson['pos'] = datajson.get('pos',0) + 1
            elif q.auto_evaluate == '0':
                datajson['neg'] = datajson.get('neg',0) + 1
        for j in datajson:
            item = {}
            if j == 'pos':
                item['name'] = '积极'
            else:
                item['name'] = '消极'
            item['value'] = datajson.get(j,0)
            resdata.append(item)
    except Exception as e:
        print(e)
    return resdata

def comparefeelings(becomparedlist,comparetolist):
    responsedata = {}
    responsedata['resbecomparedlist'] = []
    responsedata['rescomparetolist'] = []
    for b in becomparedlist:
        item = {}
        item['series'] = b
        item['data'] = comparegetfeelingsdatabyseries(b)
        responsedata['resbecomparedlist'].append(item)
    for c in comparetolist:
        item = {}
        item['series'] = c
        item['data'] = comparegetfeelingsdatabyseries(c)
        responsedata['rescomparetolist'].append(item)
    return responsedata

def comparegetdata(series,category):
    resdata = []
    try:
        q_set = AutohomeData.objects.filter(auto_series=series,auto_category=category)
        cnt = {}
        for q in q_set:
            cnt[q.auto_tag] = cnt.get(q.auto_tag,0) + 1
        for i in cnt:
            item = {}
            item['name'] = i
            item['value'] = cnt.get(i,0)
            resdata.append(item)
    except Exception as e:
        print(e)
    return resdata

def comparebycategory(becomparedlist,comparetolist,category):
    responsedata = {}
    responsedata['resbecomparedlist'] = []
    responsedata['rescomparetolist'] = []
    for b in becomparedlist:
        item = {}
        item['series'] = b
        item['data'] = comparegetdata(b,category)
        responsedata['resbecomparedlist'].append(item)
    for c in comparetolist:
        item = {}
        item['series'] = c
        item['data'] = comparegetdata(c,category)
        responsedata['rescomparetolist'].append(item)
    return responsedata

def handlecompareto(request):
    if request.method == "POST":
        tp = request.POST['type']
        becomparedlist = request.POST.getlist('becomparedlist[]')
        comparetolist = request.POST.getlist('comparetolist[]')
        allresponse = {}
        if tp == 'feelings':
            allresponse['type'] = tp
            allresponse['data'] = comparefeelings(becomparedlist,comparetolist)
        else:
            allresponse['type'] = tp
            allresponse['data'] = comparebycategory(becomparedlist,comparetolist,tp)
        return JsonResponse(allresponse)

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
    if request.method == 'POST':
        resdata = {}
        resdata['ok'] = 0
        try:
            q = AutohomeData.objects.all().delete()
            resdata['ok'] = 1
            print('success!')
        except Exception as e:
            resdata['ok'] = 0
        return JsonResponse(resdata)

def autohomedata(request):
    """
    将汽车之家数据存入数据库
    """
    if request.method == 'POST':
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
        return JsonResponse({'ok':1})

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

def weiboshow(request):
    """
    获取三种车系的词云数据，总体页面
    """
    if request.method == 'POST':
        cur_brand = request.POST['curbrand']
        cur_brand = '#' + cur_brand
        res = get_data(cur_brand)
        return JsonResponse(res)
    else:
        return render(request,'weiboshow.html',csrf(request))

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
