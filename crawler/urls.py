from os import name
from django.urls import path
from . import views

app_name = 'crawler'
urlpatterns = [

    path('index/', views.index, name='index'),
    path('weiboshow/',views.weiboshow,name='weiboshow'),
    path('autohome/',views.autohomehtml,name='autohome'),
    path('ahshow/',views.ahshow,name='ahshow'),
    path('compare/',views.compareseries,name='compareseries'),

    ## api 区域
    path('getlegend/',views.getlegend,name='getlegend'),
    path('compareto/',views.compareto,name='compareto'),
    path('handleahshow/',views.handleahshow,name='handleahshow'),
    path('handlecategory/',views.handlecategory,name='handlecategory'),
    path('showgetdata/',views.showgetdata,name='showgetdata'),
    path('handlecompareto/',views.handlecompareto,name='handlecompareto'),
    path('delete/',views.deleteautohome, name="delete"),
    path('autohomedata/',views.autohomedata, name="autohomedata"),
    path('startcrawler/',views.startcrawler, name="scrawler"),

    # path('show/',views.show, name='show'),
    # path('toptopic/',views.toptopic,name='toptopic'),
    # path('echarts/',views.echarts,name='echarts'),
    # path('singleshow/<tag>',views.singleshow,name='singleshow'),
    # path('autohomeapi/',views.autohomeapi,name='autohomeapi')
]