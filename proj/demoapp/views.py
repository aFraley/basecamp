from rest_framework import viewsets
from django.shortcuts import render
from django.db.models import Count, Max, Min
from django.utils.timezone import get_current_timezone

from datetime import datetime, timedelta
from collections import Counter
import json

from .serializers import TweetSerializer, TweetDateSerializer
from .models import Tweet, TweetSort, TweetCount


class TweetViewSet(viewsets.ModelViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer


class TweetDateViewSet(viewsets.ModelViewSet):
    queryset = Tweet.objects.values('tweet_date')
    serializer_class = TweetDateSerializer


def index(request):
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

    jobs = TweetSort.objects.filter(twt_date__lte=datetime.now())\
        .extra({"hour": "date_trunc('hour', twt_date)"}).values(
        "hour").order_by('-twt_date').annotate(count=Count("id"))

    print(jobs[0])

    twt_counts = TweetCount.objects.all().extra({"day": "date_trunc('day', date)"}).order_by('day')

    context = {
        'query': query,
        'start': start,
        'stop': stop,
        'distance': distance,
        'status': output,
        'how_many': how_many,
        'cnt': cnt,
        'max': twt_max['tweet_id__min'],
        'test': jobs[:3],
        'count': twt_counts[:3]
    }
    return render(request, 'demoapp/test.html', context)
