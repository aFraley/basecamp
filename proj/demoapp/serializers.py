from rest_framework import serializers

from .models import Tweet


class TweetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tweet
        fields = (
            'tweet_id',
            'tweet_date',
            'tweet_source',
            'tweet_favorite_cnt',
            'tweet_retweet_cnt',
            'tweet_text',
        )


class TweetDateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tweet
        fields = (
            'tweet_date',
        )
