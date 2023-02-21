from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func


class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_followed = db.Column(db.DateTime(timezone=True), default=func.now())

class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(150),unique=True)
    username = db.Column(db.String(150),unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True),default=func.now())
    posts =  db.relationship("Post", backref="user",cascade="all, delete")
    comments =  db.relationship("Comment", backref="user",cascade="all, delete")
    likes =  db.relationship("Like", backref="user",cascade="all, delete")
    followers = db.relationship("Follower", foreign_keys=[Follower.user_id], backref="followed_user", lazy="dynamic")
    following = db.relationship("Follower", foreign_keys=[Follower.follower_id], backref="follower", lazy="dynamic")


class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    text =db.Column(db.Text,nullable=False)
    date_created = db.Column(db.DateTime(timezone=True),default=func.now())
    author = db.Column(db.Integer,db.ForeignKey('user.id'),nullable = False)
    comments =  db.relationship("Comment", backref="post",cascade="all, delete")
    likes =  db.relationship("Like", backref="post",cascade="all, delete")

    
class Comment(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    text =db.Column(db.String(20),nullable=False)
    date_created = db.Column(db.DateTime(timezone=True),default=func.now())
    author = db.Column(db.Integer,db.ForeignKey('user.id'),nullable = False)
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'),nullable = False)
    
class Like(db.Model):  
    id = db.Column(db.Integer,primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True),default=func.now())
    author = db.Column(db.Integer,db.ForeignKey('user.id'),nullable = False)
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'),nullable = False)
    


