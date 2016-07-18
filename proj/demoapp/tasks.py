"""Tasks for Celery"""
from django.db import IntegrityError
from django.db.models import Count, Min

from celery import shared_task
import tweepy
from datetime import datetime, timedelta
import json

from .models import Tweet, TweetSort, TweetCount


with open('/home/alan/srv/basecamp/twt_auth.json', 'r') as f:
    auth_data = json.load(f)

app_0 = auth_data[0]['app_0']
app_1 = auth_data[1]['app_1']

# app-0 auth data
CONSUMER_KEY = app_0['consumer_key']
CONSUMER_SECRET = app_0['consumer_secret']
ACCESS_TOKEN = app_0['access_token']
ACCESS_TOKEN_SECRET = app_0['access_token_secret']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# app_1 auth data
CONSUMER_KEY_1 = app_1['consumer_key']
CONSUMER_SECRET_1 = app_1['consumer_secret']
ACCESS_TOKEN_1 = app_1['access_token']
ACCESS_TOKEN_SECRET_1 = app_1['access_token_secret']

auth_1 = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth_1.set_access_token(ACCESS_TOKEN_1, ACCESS_TOKEN_SECRET_1)

api_1 = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


@shared_task(name='get_recent')
def get_recent():
    """Get today's tweets, disregard the min id already in the database."""
    # Hit up the Twitter search API
    tweets = api_1.search(q='#python', count=100)

    # Process and store these tweets
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
            # Check for duplicates, based on the Tweet's id.
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


@shared_task(name='count_tweets')
def count_tweets():
    """Count the scrubbed tweets--made easier by scrubbing excess data from the DateTimeField()."""

    # Query the TweetSort db and count objects based on their DateTimeField().
    counted_tweets = TweetSort.objects.filter(twt_date__lte=datetime.now())\
        .extra({"hour": "date_trunc('hour', twt_date)"}).values(
        "hour").order_by().annotate(count=Count("id"))

    # Flush the TweetCount db before applying new data.
    TweetCount.objects.all().delete()

    # Store tweet count data in TweetCount db.
    for row in counted_tweets:
        TweetCount.objects.create(date=row['hour'], count=row['count'])


@shared_task(name='scrub_tweets')
def scrub_tweets():
    """Scrub the tweet_date data to eliminate minutes and seconds from the DateTimeField()"""
    query = Tweet.objects.values('tweet_date', 'tweet_id').order_by('tweet_date')

    scrubbed_tweets = []
    for tweet in query:
        row = (tweet['tweet_date'].replace(minute=0, second=0, microsecond=0) - timedelta(hours=5), tweet['tweet_id'])
        scrubbed_tweets.append(row)

    TweetSort.objects.all().delete()
    for row in scrubbed_tweets:
        TweetSort.objects.create(twt_date=row[0], twt_id=row[1])


@shared_task(name='clean_tweetdb')
def clean_tweetdb():
    """Eliminate Tweets old tweets."""
    return Tweet.objects.filter(tweet_date__lte=datetime.now() - timedelta(days=8)).delete()


@shared_task(name='get_tweets')
def get_tweets():
    """Get some tweets from the twitter api and store them to the db."""

    # Return Tweets that are older than the min tweet_id.
    db_tweets = Tweet.objects.all()
    max_id = db_tweets.aggregate(Min('tweet_id'))
    tweets = api.search(
        q='#python',
        max_id=max_id,
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
    get_tweets.s().apply_async()
    clean_tweetdb.s().apply_async()
    scrub_tweets.s().apply_async()
    count_tweets.s().apply_async()
