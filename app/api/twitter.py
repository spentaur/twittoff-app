import tweepy
from decouple import config

TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),
                                   config('TWITTER_CONSUMER_SECRET'))

TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                              config('TWITTER_ACCESS_TOKEN_SECRET'))

TWITTER = tweepy.API(TWITTER_AUTH)


def twitter_user_exists(username):
    try:
        TWITTER.get_user(username)
        return True
    except tweepy.TweepError as e:
        return False
