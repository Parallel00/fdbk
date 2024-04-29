from flask_sqlalchemy import SQLAlchemy as datbs
from flask_bcrypt import Bcrypt

datbs = SQLAlchemy()
bcrypt = Bcrypt()

class User(datbs.Model):
    __tablename__ = "users"

    id = datbs.Column(datbs.Integer, primary_key=True)
    username = datbs.Column(datbs.String(20), nullable=False, unique=True)
    email = datbs.Column(datbs.String(50), nullable=False)
    password_hash = datbs.Column(datbs.String(128), nullable=False)
    first_name = datbs.Column(datbs.String(30), nullable=False)
    last_name = datbs.Column(datbs.String(30), nullable=False)
    feedback = datbs.relationship("Feedback", backref="user", cascade="all,delete")

    def __init__(slf, username, email, password, first_name, last_name):
        slf.username = username
        slf.email = email
        slf.set_password(password)
        slf.first_name = first_name
        slf.last_name = last_name

    def set_password(slf, password):
        slf.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(slf, password):
        return bcrypt.check_password_hash(slf.password_hash, password)

    @classmethod
    def register(cls, username, email, password, first_name, last_name):
        user = cls(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        datbs.session.add(user)
        datbs.session.commit()
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None


class Feedback(datbs.Model):
    __tablename__ = "feedback"

    id = datbs.Column(datbs.Integer, primary_key=True)
    title = datbs.Column(datbs.String(100), nullable=False)
    content = datbs.Column(datbs.Text, nullable=False)
    user_id = datbs.Column(datbs.Integer, datbs.ForeignKey('users.id'), nullable=False)

    def __init__(slf, title, content, user_id):
        slf.title = title
        slf.content = content
        slf.user_id = user_id

    @classmethod
    def post_feedback(cls, title, content, user_id):
        feedback = cls(title=title, content=content, user_id=user_id)
        datbs.session.add(feedback)
        datbs.session.commit()
        return feedback
