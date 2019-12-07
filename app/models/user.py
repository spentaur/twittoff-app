from app.extensions import db
from app.controllers.twitter import TWITTER
from app.controllers.basilica import BASILICA
from tqdm import tqdm
from .tweet import Tweet


class User(db.Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(500), unique=True, nullable=False)
    tweet_count = db.Column(db.BigInteger(), nullable=False, default=0)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(),
                           server_onupdate=db.func.now())

    @staticmethod
    def add_user(username):
        user = User.query.filter_by(username=username).first()
        twitter_user = TWITTER.get_user(username)

        # get i think 3200 tweets?
        timeline = TWITTER.user_timeline(username, count=200,
                                         exclude_replies=False,
                                         include_rts=False,
                                         tweet_mode='extended')
        earliest_tweet = min(timeline, key=lambda x: x.id).id
        print("getting tweets before:", earliest_tweet)

        if user:
            Tweet.query.filter_by(user_id=user.id).delete()

        while True:
            tweets = TWITTER.user_timeline(username, count=200,
                                           exclude_replies=False,
                                           include_rts=False,
                                           max_id=earliest_tweet,
                                           tweet_mode='extended')
            if not tweets:
                break
            new_earliest = min(tweets, key=lambda x: x.id).id

            if new_earliest == earliest_tweet:
                break
            else:
                earliest_tweet = new_earliest
                print("getting tweets before:", earliest_tweet)
                timeline += tweets

        timeline = {status.id: status for status in timeline}
        print("total num of tweets:", len(timeline))

        if not user:
            print("adding new user")
            user_fields = {
                'id':          twitter_user.id,
                'name':        twitter_user.name,
                'username':    twitter_user.screen_name,
                'tweet_count': len(timeline)

            }
            user = User(**user_fields)
            db.session.add(user)

        else:
            print("updating user tweet count")
            user.tweet_count = len(timeline)

        tweets = [status.full_text for status in timeline.values()]
        print("embedding tweets")
        with BASILICA as c:
            embeddings = list(c.embed_sentences(tweets, model="twitter"))

        print("adding tweets")

        for status, embedding in zip(timeline.values(), embeddings):
            tweet_data = {
                'id':        status.id,
                'text':      status.full_text[:500],
                'embedding': embedding,
                'user_id':   user.id
            }
            db.session.add(Tweet(**tweet_data))

        print("done")
        db.session.commit()

        return user

    @staticmethod
    def get_newest():
        return User.query.order_by(User.id.desc()).limit(20).all()
