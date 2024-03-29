from app.extensions import db
from app.api.twitter import TWITTER
from .tweet import Tweet
from sqlalchemy import func
from sqlalchemy.orm import relationship


class User(db.Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(500), unique=True, nullable=False)
    tweet_count = db.Column(db.BigInteger(), nullable=False, default=0)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(),
                           onupdate=db.func.now())

    @staticmethod
    def add_user(username):
        print(f"adding {username} to database...")
        # check if user already exists
        user = User.query.filter(
            func.lower(User.username) == func.lower(username)).first()
        # get twitter user
        twitter_user = TWITTER.get_user(username)

        if user:

            # if user already exists, delete all their tweets
            # because i'm going to get them again
            Tweet.query.filter_by(user_id=user.id).delete()
        else:
            # if user doesn't exist, add them
            user_fields = {
                'id':       twitter_user.id,
                'name':     twitter_user.name,
                'username': twitter_user.screen_name

            }
            user = User(**user_fields)
            db.session.add(user)

        db.session.commit()
        print(f"{username} has been added!")
        print("\n")

        return user

    @staticmethod
    def get_newest():
        return User.query.order_by(User.updated_on.desc()).limit(20).all()

    def get_newest_tweets(self):
        return self.tweets.limit(20)
