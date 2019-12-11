from flask import Blueprint
from app.models.user import User
from app.models.tweet import Tweet
import numpy as np
from sklearn.linear_model import SGDClassifier
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as rt
from app.api.basilica import BASILICA
from app.forms.PredictTweetForm import PredictTweetForm
from flask import render_template
from app.extensions import db
from sqlalchemy import func
import collections
import pprint as pp

blueprint = Blueprint('predict', __name__)


@blueprint.route('/predict', methods=['GET', 'POST'])
def predict():
    form = PredictTweetForm()

    users_dict = None

    if form.validate_on_submit():
        with BASILICA as c:
            embedding = np.array(c.embed_sentence(form.tweet.data,
                                                  model="twitter")).reshape(1,
                                                                            -1)

        sess = rt.InferenceSession("app/ml_models/tweet.onnx")
        input_name = sess.get_inputs()[0].name
        prob_name = sess.get_outputs()[1].name
        prob_rt = sess.run([prob_name],
                           {input_name: embedding.astype(np.float32)})[0][0]

        users = User.query.all()
        users_dict = {}
        for user in users:
            users_dict[1 / (1 + np.exp(-prob_rt[user.id]))] = {
                'name':     user.name,
                'username': user.username,
                'prob':     prob_rt[user.id]
            }

        users_dict = collections.OrderedDict(sorted(users_dict.items(),
                                                    reverse=True))

    return render_template('predict/index.html', form=form,
                           results=users_dict)


def train():
    print("training model...")
    tweets = Tweet.query.all()

    q = db.session.query(User)
    if get_count(q) > 1:
        data = np.array(
            [np.hstack([tweet.embedding, tweet.user_id]) for tweet in tweets])

        np.random.shuffle(data)

        features = data[:, :-1]
        target = data[:, -1]

        clf = SGDClassifier(loss='modified_huber', penalty='l2',
                            alpha=0.01, random_state=42,
                            max_iter=2000)
        clf.fit(features, target)
        print("model fit!")

        predicted = clf.predict(features)
        print("sklearn score:", np.mean(predicted == target))

        initial_type = [('float_input', FloatTensorType([None, 768]))]
        onx = convert_sklearn(clf, initial_types=initial_type)

        with open("app/ml_models/tweet.onnx", "wb") as f:
            f.write(onx.SerializeToString())

        print("model saved to onnx!")

        sess = rt.InferenceSession("app/ml_models/tweet.onnx")
        input_name = sess.get_inputs()[0].name
        label_name = sess.get_outputs()[0].name
        pred_onx = sess.run([label_name],
                            {input_name: features.astype(np.float32)})[0]

        print("onnx score:", np.mean(pred_onx == target))
        print("\n")
    else:
        print("not enough users")
        print("\n")


def get_count(q):
    # this shouldn't be here but o well
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count
