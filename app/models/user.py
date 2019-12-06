from app.extensions import db


class User(db.Model):
    id = db.Column(db.BigInteger(), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    tweet_count = db.Column(db.BigInteger(), nullable=False, default=0)

    @staticmethod
    def add_user(username):
        instance = User.query.filter_by(username=username).first()
        if not instance:
            instance = User(username=username)
            db.session.add(instance)
            db.session.commit()

        return instance

    @staticmethod
    def get_ten_newest():
        return User.query.order_by(User.id.desc()).limit(10).all()
