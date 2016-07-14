from django.db import IntegrityError
from django.db.models import Count

from celery import shared_task
import tweepy
from collections import Counter
from datetime import datetime, timedelta
import json

from .models import Tweet, TweetSort, TweetCount

CONSUMER_KEY = 'Vp7FVQLSwESvE9oTQruw0TnhW'
CONSUMER_SECRET = 'miy6EsGklNYxAaVn37vTjAVGwP0c67IOyuY71AAyL1p2Ba4VPN'
ACCESS_TOKEN = '1952022900-5WAHk6l5d3GllFtqDPaucSpnraIokE6hU7aBxNJ'
ACCESS_TOKEN_SECRET = 'ekONOf6QxJG6Lq3k2kznfQ16x12BGm909wckYFcP8SlYZ'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


@shared_task(name='count_test')
def count_test():
    counted_tweets = TweetSort.objects.filter(twt_date__lte=datetime.now())\
        .extra({"hour": "date_trunc('hour', twt_date)"}).values(
        "hour").order_by().annotate(count=Count("id"))

    TweetCount.objects.all().delete()

    for row in counted_tweets:
        TweetCount.objects.create(date=row['hour'], count=row['count'])


@shared_task(name='count_tweets')
def count_tweets():
    scrubbed = TweetSort.objects.values('twt_date')
    output = scrubbed
    a_list = [str(row['twt_date']) for row in output]
    cnt = Counter(a_list)

    for key, value in cnt.items():
        TweetCount.objects.create(date=key, count=value)


@shared_task(name='scrub_tweets')
def scrub_tweets():
    query = Tweet.objects.values('tweet_date', 'tweet_id').order_by('tweet_date')

    scrubbed_tweets = []
    for tweet in query:
        row = (tweet['tweet_date'].replace(minute=0, second=0, microsecond=0), tweet['tweet_id'])
        scrubbed_tweets.append(row)

    for row in scrubbed_tweets:
        TweetSort.objects.create(twt_date=row[0], twt_id=row[1])


@shared_task(name='clean_tweetdb')
def clean_tweetdb():
    return Tweet.objects.filter(tweet_date__lte=datetime.now() - timedelta(days=8)).delete()


@shared_task(name='get_tweets')
def get_tweets():
    """Get some tweets from the twitter api and store them to the db."""
    db_tweets = Tweet.objects.all()
    # max_id = min([tweet.tweet_id for tweet in db_tweets])
    tweets = api.search(
        q='#python',
        # max_id=max_id,
        count=100
    )
    tweets_id = [tweet.id for tweet in tweets]
    tweets_date = [tweet.created_at for tweet in tweets]
    tweets_source = [tweet.source for tweet in tweets]
    tweets_favorite_cnt = [tweet.favorite_count for tweet in tweets]
    tweets_retweet_cnt = [tweet.retweet_count for tweet in tweets]
    tweets_text = [tweet.text for tweet in tweets]

    for i, j, k, l, m, n in zip(
            tweets_id,
            tweets_date,
            tweets_source,
            tweets_favorite_cnt,
            tweets_retweet_cnt,
            tweets_text,
    ):
        try:
            Tweet.objects.create(
                tweet_id=i,
                tweet_date=j,
                tweet_source=k,
                tweet_favorite_cnt=l,
                tweet_retweet_cnt=m,
                tweet_text=n,
            )
        except IntegrityError:
            pass


@shared_task(name='pulse')
def pulse():
    # get_tweets.s().apply_async()
    # clean_tweetdb.s().apply_async()
    # scrub_tweets.s().apply_async()
    count_tweets.s().apply_async()
