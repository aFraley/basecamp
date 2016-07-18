from rest_framework import viewsets
from django.shortcuts import render
from django.db.models import Count, Max, Min
from django.utils.timezone import get_current_timezone
from django.core.serializers.json import DjangoJSONEncoder

from datetime import datetime, timedelta
from collections import Counter
import json
import pygal

from .serializers import TweetSerializer, TweetDateSerializer, TweetCountSerializer
from .models import Tweet, TweetSort, TweetCount


class TweetViewSet(viewsets.ModelViewSet):
    """REST viewset for a main db"""
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer


class TweetDateViewSet(viewsets.ModelViewSet):
    queryset = Tweet.objects.values('tweet_date')
    serializer_class = TweetDateSerializer


class TweetCountViewSet(viewsets.ModelViewSet):
    queryset = TweetCount.objects.all().extra({"day": "date_trunc('day', date)"}).order_by('day')
    serializer_class = TweetCountSerializer


def index(request):
    """Logic testing for our views"""
    """Test the data."""
    query = Tweet.objects.all()
    start = query.aggregate(Max('tweet_date'))
    stop = query.aggregate(Min('tweet_date'))
    distance = start['tweet_date__max'] - stop['tweet_date__min']
    how_many = query.count()
    scrubbed = TweetSort.objects.values('twt_date')
    output = scrubbed[:3]
    a_list = [str(row['twt_date']) for row in output]
    cnt = Counter(a_list)

    twt_max = query.aggregate(Min('tweet_id'))

    twt_counts = TweetCount.objects.all().extra({
        'day': "date_trunc('day', date)",
        'hour': "date_trunc('hour', date)",
    }).order_by('-day', '-hour')

    hello = 'Hell the fuck lo!'

    context = {
        'query': query,
        'start': start,
        'stop': stop,
        'distance': distance,
        'status': output,
        'how_many': how_many,
        'cnt': cnt,
        'max': twt_max['tweet_id__min'],
        'count': twt_counts[:10],
        'hello': hello,
    }
    return render(request, 'demoapp/test.html', context)


def charts(request):
    """Logic for our charts view"""
    query = list(TweetCount.objects.filter(date__day=18).extra({
        "day": "date_trunc('day', date)",
        "hour": "date_trunc('hour', date)",
    }).values('date', 'count').order_by('-day', '-hour'))

    hist = pygal.HorizontalBar()
    hist.title = 'Tweets Histogram for #python'
    for i in range(len(query[:10])):
        hist.add(query[i]['date'].ctime(), int(query[i]['count']))

    context = {
        'hello': 'Hello!',
        'chart': hist.render_data_uri(),
    }
    return render(request, 'demoapp/charts.html', context)
