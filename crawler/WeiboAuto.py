#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import math
import sys
import random
from collections import OrderedDict
from datetime import date, datetime, timedelta
from time import sleep

import requests
from lxml import etree
from bs4 import BeautifulSoup
from tqdm import tqdm

class WeiboAuto(object):
    def __init__(self):
        """Weibo类初始化""" 
        # 微博cookie，可填可不填
        cookie = '' 
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        self.headers = {'User_Agent': user_agent, 'Cookie': cookie}
        self.since_date = ''
        self.start_date = ''  # 获取用户第一条微博时的日期
        self.start_page = 1
        self.query = ''
        self.got_count = 0  # 存储爬取到的微博数
        self.weibo = []  # 存储爬取到的所有微博信息
        self.weibo_id_list = []  # 存储爬取到的所有微博id

    def is_date(self, since_date):
        """判断日期格式是否正确"""
        try:
            datetime.strptime(since_date, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def get_json(self, params):
        """获取网页中json数据"""
        url = 'https://m.weibo.cn/api/container/getIndex?'
        r = requests.get(url,
                         params=params,
                         headers=self.headers,
                         verify=False) 
        return r.json()

    def get_comments_json(self, page):
        """获取网页中微博json数据"""
        params = {
            'containerid': '100103type=1&q=' + self.query,
            'page_type': 'searchall'
        }
        params['page'] = page
        js = self.get_json(params)
        return js

    def get_long_weibo(self, id):
        """获取长微博"""
        for i in range(5):
            url = 'https://m.weibo.cn/detail/%s' % id
            html = requests.get(url, headers=self.headers, verify=False).text
            html = html[html.find('"status":'):]
            html = html[:html.rfind('"hotScheme"')]
            html = html[:html.rfind(',')]
            html = '{' + html + '}'
            js = json.loads(html, strict=False)
            weibo_info = js.get('status')
            if weibo_info:
                weibo = self.parse_weibo(weibo_info)
                return weibo
            sleep(random.randint(6, 10))

    def get_location(self, selector):
        """获取微博发布位置"""
        location_icon = 'timeline_card_small_location_default.png'
        span_list = selector.xpath('//span')
        location = ''
        for i, span in enumerate(span_list):
            if span.xpath('img/@src'):
                if location_icon in span.xpath('img/@src')[0]:
                    location = span_list[i + 1].xpath('string(.)')
                    break
        return location

    def get_article_url(self, selector):
        """获取微博中头条文章的url"""
        article_url = ''
        text = selector.xpath('string(.)')
        if text.startswith(u'发布了头条文章'):
            url = selector.xpath('//a/@data-url')
            if url and url[0].startswith('http://t.cn'):
                article_url = url[0]
        return article_url

    def get_topics(self, selector):
        """获取参与的微博话题"""
        span_list = selector.xpath("//span[@class='surl-text']")
        topics = ''
        topic_list = []
        for span in span_list:
            text = span.xpath('string(.)')
            if len(text) > 2 and text[0] == '#' and text[-1] == '#':
                topic_list.append(text[1:-1])
        if topic_list:
            topics = ','.join(topic_list)
        return topics
    def parse_text(self,text_body):
        """只获取正文内容"""
        soup = BeautifulSoup(text_body,"html5lib")
        [s.extract() for s in soup("a")]
        [s.extract() for s in soup("span")]
        res = soup.body.get_text()
        return res

    def get_at_users(self, selector):
        """获取@用户"""
        a_list = selector.xpath('//a')
        at_users = ''
        at_list = []
        for a in a_list:
            if '@' + a.xpath('@href')[0][3:] == a.xpath('string(.)'):
                at_list.append(a.xpath('string(.)')[1:])
        if at_list:
            at_users = ','.join(at_list)
        return at_users

    def string_to_int(self, string):
        """字符串转换为整数"""
        if isinstance(string, int):
            return string
        elif string.endswith(u'万+'):
            string = int(string[:-2] + '0000')
        elif string.endswith(u'万'):
            string = int(string[:-1] + '0000')
        return int(string)

    def standardize_date(self, created_at):
        """标准化微博发布时间"""
        if u'刚刚' in created_at:
            created_at = datetime.now().strftime('%Y-%m-%d')
        elif u'分钟' in created_at:
            minute = created_at[:created_at.find(u'分钟')]
            minute = timedelta(minutes=int(minute))
            created_at = (datetime.now() - minute).strftime('%Y-%m-%d')
        elif u'小时' in created_at:
            hour = created_at[:created_at.find(u'小时')]
            hour = timedelta(hours=int(hour))
            created_at = (datetime.now() - hour).strftime('%Y-%m-%d')
        elif u'昨天' in created_at:
            day = timedelta(days=1)
            created_at = (datetime.now() - day).strftime('%Y-%m-%d')
        else:
            created_at = created_at.replace('+0800 ', '')
            temp = datetime.strptime(created_at, '%c')
            created_at = datetime.strftime(temp, '%Y-%m-%d')
        return created_at

    def standardize_info(self, weibo):
        """标准化信息，去除乱码"""
        for k, v in weibo.items():
            if 'bool' not in str(type(v)) and 'int' not in str(
                    type(v)) and 'list' not in str(
                        type(v)) and 'long' not in str(type(v)):
                weibo[k] = v.replace(u'\u200b', '').encode(
                    sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding)
        return weibo

    def parse_weibo(self, weibo_info):
        weibo = OrderedDict()
        if weibo_info['user']:
            weibo['user_id'] = weibo_info['user']['id']
            weibo['screen_name'] = weibo_info['user']['screen_name']
        else:
            weibo['user_id'] = ''
            weibo['screen_name'] = ''
        weibo['id'] = weibo_info['id']
        weibo['bid'] = weibo_info['bid']
        text_body = weibo_info['text']
        selector = etree.HTML(text_body)
        weibo['text'] = self.parse_text(text_body)
        weibo['location'] = self.get_location(selector)
        weibo['created_at'] = weibo_info['created_at']
        weibo['source'] = weibo_info['source']
        weibo['attitudes_count'] = self.string_to_int(weibo_info.get('attitudes_count', 0))
        weibo['comments_count'] = self.string_to_int(weibo_info.get('comments_count', 0))
        weibo['reposts_count'] = self.string_to_int(weibo_info.get('reposts_count', 0))
        weibo['topics'] = self.get_topics(selector)
        weibo['at_users'] = self.get_at_users(selector)
        return self.standardize_info(weibo)

    def print_one_weibo(self, weibo):
        """打印一条微博"""
        try:
            print('发布此微博用户id：{}'.format(weibo['user_id']))
            print('发布此微博用户名：{}'.format(weibo['screen_name']))
            print('微博id：{}'.format(weibo['id']))
            print('微博正文：{}'.format(weibo['text']))
            print('微博位置：{}'.format(weibo['location']))
            print('发布时间：{}'.format(weibo['created_at']))
            print('发布来源：{}'.format(weibo['source']))
            print('点赞数：{}'.format(weibo['attitudes_count']))
            print('评论数：{}'.format(weibo['comments_count']))
            print('转发数：{}'.format(weibo['reposts_count']))
            print('所属主题：{}'.format(weibo['topics']))
            print('@用户：{}'.format(weibo['at_users']))
        except OSError:
            pass

    def print_weibo(self, weibo):
        """打印微博，若为转发微博，会同时打印原创和转发部分"""
        if weibo.get('retweet'):
            print('*' * 100)
            print('转发部分：')
            self.print_one_weibo(weibo['retweet'])
        print('*' * 100)
        print('原创部分：')
        self.print_one_weibo(weibo)
        print('-' * 100)

    def get_one_weibo(self, info):
        """获取一条微博的全部信息"""
        try:
            weibo_info = info['mblog']
            weibo_id = weibo_info['id']
            retweeted_status = weibo_info.get('retweeted_status')
            is_long = True if weibo_info.get('pic_num') > 9 else weibo_info.get('isLongText')
            if retweeted_status and retweeted_status.get('id'):  # 转发
                retweet_id = retweeted_status.get('id')
                is_long_retweet = retweeted_status.get('isLongText')
                if is_long:
                    weibo = self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
                if is_long_retweet:
                    retweet = self.get_long_weibo(retweet_id)
                    if not retweet:
                        retweet = self.parse_weibo(retweeted_status)
                else:
                    retweet = self.parse_weibo(retweeted_status)
                retweet['created_at'] = self.standardize_date(
                    retweeted_status['created_at'])
                weibo['retweet'] = retweet
            else:  # 原创
                if is_long:
                    weibo = self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
            weibo['created_at'] = self.standardize_date(weibo_info['created_at'])
            return weibo
        except Exception as e:
            print(e)

    def is_pinned_weibo(self, info):
        """判断微博是否为置顶微博"""
        weibo_info = info['mblog']
        title = weibo_info.get('title')
        if title and title.get('text') == u'置顶':
            return True
        else:
            return False

    def get_one_page(self, page):
        """获取一页的全部微博"""
        try:
            js = self.get_comments_json(page)
            if js['ok']:
                weibos = js['data']['cards']
                for w in weibos:
                    if w['card_type'] == 9:
                        wb = self.get_one_weibo(w)
                        if wb:
                            if wb['id'] in self.weibo_id_list:
                                continue
                            created_at = datetime.strptime(wb['created_at'], '%Y-%m-%d')
                            since_date = datetime.strptime(self.since_date, '%Y-%m-%d')
                            if created_at < since_date:
                                if self.is_pinned_weibo(w):
                                    continue
                                else:
                                    print(u'{}已经获取第{}页评论{}'.format(
                                        '-'*30,
                                        page,
                                        '-'*30,
                                    ))
                                    return True
                            if ('retweet' not in wb.keys()):
                                self.weibo.append(wb)
                                self.weibo_id_list.append(wb['id'])
                                self.got_count += 1
                                # self.print_weibo(wb)
                            else:
                                print(u'正在过滤转发微博')
            else:
                return True
            print(u'{}已获取{}的第{}页微博{}'.format('-' * 30, self.query, page,'-' * 30))
        except Exception as e:
            print(e)

    def get_page_count(self):
        """获取微博页数"""
        try:
            js = self.get_comments_json(1)
            page_count = 0
            if js['ok']:
                weibo_count = js['data']['cardlistInfo']['total']
                page_count = int(math.ceil(weibo_count / 10.0))
            return page_count
        except KeyError:
            print(u'程序出错\n')

    def get_pages(self):
        """获取全部微博"""
        try:
            since_date = datetime.strptime(self.since_date,'%Y-%m-%d')
            today = datetime.strptime(str(date.today()), '%Y-%m-%d')
            if since_date <= today:
                page_count = self.get_page_count()
                page1 = 0
                random_pages = random.randint(1, 5)
                self.start_date = datetime.now().strftime('%Y-%m-%d')
                pages = range(self.start_page, page_count + 1)
                for page in tqdm(pages, desc='Progress'):
                    is_end = self.get_one_page(page)
                    if is_end:
                        break

                    # 通过加入随机等待避免被限制。爬虫速度过快容易被系统限制(一段时间后限
                    # 制会自动解除)，加入随机等待模拟人的操作，可降低被系统限制的风险。默
                    # 认是每爬取1到5页随机等待6到10秒，如果仍然被限，可适当增加sleep时间
                    if (page - page1) % random_pages == 0 and page < page_count:
                        sleep(random.randint(6, 10))
                        page1 = page
                        random_pages = random.randint(1, 5)
                print(u'微博爬取完成，共爬取{}条微博'.format(self.got_count))
            else:
                print(u'请检查起始日期是否输入不合理！')
        except Exception as e:
            print(e)

    def get_weibos(self):
        return self.weibo

    def start(self,query):
        """运行爬虫"""
        self.query = query
        self.since_date = '2020-01-01'
        self.start_page = 1
        self.get_pages()

# wb = WeiboAuto()
# wb.start(query="#宝马")  # 爬取微博信息

# 宝马 奥迪 奔驰
# 微博 汽车之家论坛 知乎 汽车话题的评论 top10评论 词云正负面 前十名话题