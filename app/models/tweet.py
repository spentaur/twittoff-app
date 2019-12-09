from app.extensions import db
from app.api.twitter import TWITTER
from app.api.basilica import BASILICA


class Tweet(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.Unicode(500), nullable=False)
    embedding = db.Column(db.PickleType, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'),
                        nullable=False)
    user = db.relationship("User", backref=db.backref('tweets',
                                                      lazy='dynamic'))

    @staticmethod
    def add_user_tweets(user):
        # get first 200 tweets
        timeline = TWITTER.user_timeline(user.username, count=200,
                                         exclude_replies=False,
                                         include_rts=False,
                                         tweet_mode='extended')
        # this is for the pagination to get the rest of them
        earliest_tweet = min(timeline, key=lambda x: x.id).id

        while True:
            # this loops through and gets all the tweets i can
            tweets = TWITTER.user_timeline(user.username, count=200,
                                           exclude_replies=False,
                                           include_rts=False,
                                           max_id=earliest_tweet,
                                           tweet_mode='extended')

            if not tweets:
                # if there are no tweets, break gracefully?
                break

            new_earliest = min(tweets, key=lambda x: x.id).id

            if new_earliest == earliest_tweet:
                break
            else:
                earliest_tweet = new_earliest
                timeline += tweets

        # this is because there was some weird stuff and i was getting the
        # the same tweets multiple times ¯\_(ツ)_/¯
        timeline = {status.id: status for status in timeline}
        # update the user to have tweet count
        user.tweet_count = len(timeline)

        # embedding the tweets in big batches
        tweets = [status.full_text for status in timeline.values()]
        with BASILICA as c:
            embeddings = list(
                c.embed_sentences(tweets, model="twitter"))

        # adding all the tweets and embeddings to the db
        for status, embedding in zip(timeline.values(), embeddings):
            tweet_data = {
                'id':        status.id,
                'text':      status.full_text[:500],
                'embedding': embedding,
                'user_id':   user.id
            }
            db.session.add(Tweet(**tweet_data))

        db.session.commit()

    @staticmethod
    def get_ten_newest():
        return Tweet.query.order_by(Tweet.id.desc()).limit(10).all()
