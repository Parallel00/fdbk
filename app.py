from flask import Flask, render_template, redirect, session, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///flask-feedback.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "ITSASECRET"
datbs = SQLAlchemy(app)

class User(datbs.Model):
    id = datbs.Column(datbs.Integer, primary_key=True)
    username = datbs.Column(datbs.String(50), unique=True, nullable=False)
    password = datbs.Column(datbs.String(50), nullable=False)
    first_name = datbs.Column(datbs.String(50), nullable=False)
    last_name = datbs.Column(datbs.String(50), nullable=False)
    email = datbs.Column(datbs.String(100), nullable=False)
    feedbacks = datbs.relationship('Feedback', backref='user', lazy=True)

    @classmethod
    def register(cls, username, password, first_name, last_name, email):
        user = cls(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
        datbs.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username, password=password).first()
        return user

class Feedback(datbs.Model):
    id = datbs.Column(datbs.Integer, primary_key=True)
    title = datbs.Column(datbs.String(100), nullable=False)
    content = datbs.Column(datbs.Text, nullable=False)
    user_id = datbs.Column(datbs.Integer, datbs.ForeignKey('user.id'), nullable=False)

datbs.create_all()

@app.route("/")
def homepage():
    return redirect("/register")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']

        user = User.register(username, password, first_name, last_name, email)
        datbs.session.commit()
        session['username'] = user.username
        return redirect(f"/users/{user.username}")

    return render_template("users/register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")

    return render_template("users/login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

@app.route("/users/<username>")
def show_user(username):
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.filter_by(username=username).first()
    return render_template("users/show.html", user=user)

if __name__ == '__main__':
    app.run(debug=True)
