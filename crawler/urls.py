from django.urls import path
from . import views

app_name = 'crawler'
urlpatterns = [
    path('', views.index, name='index'),
    path('startcrawler/',views.startcrawler, name="scrawler")
]