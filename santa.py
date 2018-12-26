from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# SQLite
db = SQLAlchemy(app)

class User(db.Model):
    '''
    Main site account table
    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    kid = db.Column(db.String(20), nullable=False, default='')


# Initialize extension with your app.
app.config['SECRET_KEY'] = 'VAR_APP_SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


forbidden = [('Mariia', 'Denys'), ('Dmytro', 'Kateryna'), ('Viktoria', 'Ihor'), ('Khrystya', 'Vlad')]

# @app.route('/')
# def home():
#     # people = ['Mariia', 'Denys', 'Dmytro', 'Kateryna', 'Ihor', 'Viktoria', 'Harya', 'Khrystya', 'Vlad']
#     users = User.query.all()
#     people = []
#     for human in users:
#         people.append(human.username)

#     pairs_unique = {}

#     def pick_kid(santa):
#         kid = random.choice(people)
#         while kid == santa or (kid, santa) in forbidden or (santa, kid) in forbidden \
#             or kid in list(pairs_unique.values()):
#             kid = random.choice(people)
#         pairs_unique[santa] = kid

#     for santa in people:
#         pick_kid(santa)

#     return str(pairs_unique).replace(',', ', <br>')

@app.route('/', methods=['GET', 'POST'])
def index():
    # get all kids
    users = User.query.all()
    kids = [user.kid for user in users]
    
    # all users list
    people = []
    for human in users:
        people.append(human.username)

    def pick_kid(santa):
        kid = random.choice(people)
        while kid == santa.username or (kid, santa.username) in forbidden or (santa.username, kid) in forbidden \
            or kid in kids:
            kid = random.choice(people)

        santa.kid = kid
        db.session.commit()

    if request.method == "POST":
        email = request.form.get("email").lower()
        user = User.query.filter_by(email=email).first()
        if user:
            if not user.kid:
                pick_kid(user)

            kid = User.query.filter_by(username = user.kid).first()
            return redirect(url_for('chosen', id=user.id))
            print(kid.username)
        else:
            return 'Неправильный email'

    return render_template("index.html")


@app.route('/chosen/<int:id>', methods=['GET', 'POST'])
def chosen(id):
    try:
        # santa
        user = User.query.filter_by(id=id).first()
        # kid
        kid = User.query.filter_by(username=user.kid).first()

        username_self = user.username
        image_file_kid = url_for('static', filename='img/' + kid.image_file)
        username_kid = kid.username
        email_kid = kid.email
    except:
        return 'Шось ти не так зробив'

    return render_template("chosen.html", username_self=username_self, email_kid=email_kid, 
                            image_file_kid=image_file_kid, username_kid=username_kid)


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return 'такої сторінки нема, не мудруй з URLами', 404

if __name__ == '__main__':
    app.run(debug=True)
