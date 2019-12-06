from app.extensions import db
from app.models.user import User


class Tweet(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.Unicode(500), nullable=False)
    embedding = db.Column(db.PickleType, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'),
                        nullable=False)
    user = db.relationship("User", backref=db.backref('tweets', lazy=True))

    @staticmethod
    def add_tweet(user, tweet_body):
        user.tweet_count += 1
        tweet = Tweet(user_id=user.id, text=tweet_body)
        db.session.add(tweet)
        db.session.commit()

        return tweet

    @staticmethod
    def get_ten_newest():
        return Tweet.query.order_by(Tweet.id.desc()).limit(10).all()
