from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import requests
from flask import Flask, render_template, redirect, url_for, flash, abort
from functools import wraps
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from typing import Callable
from forms import RegisterForm, CreatePostForm, LoginForm, CommentForm, ContactForm

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_key"
Bootstrap(app)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Text: Callable
    Integer: Callable
    ForeignKey: Callable


db = MySQLAlchemy(app)

# Login Manager and User Authentication
login_manager = LoginManager()
login_manager.init_app(app)

# created a function wrapper that allowed me to make the user 1 to have admin controls
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


##TABLES Configuration
# Use relationship to connect the users to the journal database

class GymJournal(db.Model):
    __tablename__ = "journal_posts"
    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey("user_details.id"))
    author = relationship("User", back_populates="posts")

    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "user_details"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True)
    name = db.Column(db.String(200))
    password = db.Column(db.String(200))

    posts = relationship("GymJournal", back_populates="author")


db.create_all()

# Search Form for the Gym Web App Version 1
# class GymSearch(FlaskForm):
#     exc = StringField("Search exercise here", render_kw={'style': 'width: 125ch, height: 4ch '})
#     submit = SubmitField("Search")


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        exercise = request.form.get('search')

        headers = {
            "X-RapidAPI-Key": "bb8f721820msh41917aa6a4592a7p1466e2jsn11d3b1b25ada",
            "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
        }
        url = f"https://exercisedb.p.rapidapi.com/exercises/name/{exercise}"

        response = requests.request("GET", url, headers=headers)

        ex_list = response.json()  # Did not store the search json in a database because it would be repopulated often
        # might add that functionality in a new update
        return render_template("new-display.html", exercise_list=ex_list)

    return render_template("new-index.html")



# @app.route("/delete/<int:post_id>", methods=["POST", "GET"])
# def delete_post(post_id):
#     post_to_delete = Library.query.get(post_id)
#     db.session.delete(post_to_delete)
#     db.session.commit()
#     return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

