from django.conf.urls import url

from .views import index, charts

urlpatterns = [
    url(r'^$', index, name='test'),
    url(r'^charts/$', charts, name='charts')
]
