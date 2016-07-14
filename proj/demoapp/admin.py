from django.contrib import admin
from .models import Tweet, TweetSort, TweetCount

admin.site.register(Tweet)
admin.site.register(TweetSort)
admin.site.register(TweetCount)
