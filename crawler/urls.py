from django.urls import path
from . import views

app_name = 'crawler'
urlpatterns = [
    path('', views.index, name='index'),
    path('startcrawler/',views.startcrawler, name="scrawler"),
    # path('autohome/',views.autohomedata, name="autohome"),
    # path('delete/',views.deleteautohome, name="delete"),
    path('show/',views.show, name='show'),
    path('toptopic/',views.toptopic,name='toptopic'),
    path('echarts/',views.echarts,name='echarts'),
    path('singleshow/<tag>',views.singleshow,name='singleshow'),
    path('showgetdata/',views.showgetdata,name='showgetdata'),
    path('autohomeapi/',views.autohomeapi,name='autohomeapi')
]