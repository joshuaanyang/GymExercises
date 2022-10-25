from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from typing import Callable
from sqlalchemy.orm import relationship
from forms import RegisterForm, LoginForm, ContactForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_key"
Bootstrap(app)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#RAPID KEY
rapid_key = os.environ.get("RAPID-KEY")
rapid_host = os.environ.get("RAPID-HOST")

class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Text: Callable
    Integer: Callable
    ForeignKey: Callable


db = MySQLAlchemy(app)

## Login Manager and User Authentication
login_manager = LoginManager()
login_manager.init_app(app)


## created a function wrapper that allowed me to make the user 1 to have admin controls
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
## Use relationship to connect the users to the journal database

class GymJournal(db.Model):
    __tablename__ = "journal_posts"
    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey("user_details.id"))
    author = relationship("User", back_populates="posts")

    month = db.Column(db.String(250), nullable=False)
    day = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "user_details"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True)
    name = db.Column(db.String(200))
    password = db.Column(db.String(200))

    posts = relationship("GymJournal", back_populates="author")


db.create_all()


## Search Form for the Gym Web App Version 1
# class GymSearch(FlaskForm):
#     exc = StringField("Search exercise here", render_kw={'style': 'width: 125ch, height: 4ch '})
#     submit = SubmitField("Search")


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        exercise = request.form.get('search')

        headers = {
            "X-RapidAPI-Key": "bb8f721820msh41917aa6a4592a7p1466e2jsn11d3b1b25ada",
            "X-RapidAPI-Host": rapid_host
        }
        url = f"https://exercisedb.p.rapidapi.com/exercises/name/{exercise}"

        response = requests.request("GET", url, headers=headers)

        ex_list = response.json()  # Did not store the search json in a database because it would be repopulated often
        # might add that functionality in a new update
        return render_template("new-display.html", exercise_list=ex_list, current_user=current_user)

    return render_template("new-index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        if User.query.filter_by(email=register_form.email.data).first():
            flash("You've signed up with that email already, try logging in instead.")
            return redirect(url_for('login'))
        else:
            new_user = User(
                name=register_form.name.data,
                email=register_form.email.data,
                password=generate_password_hash(method="pbkdf2:sha256", password=register_form.password.data,
                                                salt_length=8)
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home', current_user=current_user))
    return render_template("new-sign-up.html", form=register_form)


@app.route('/login', methods=["GET", "POST"])
def login():
    loginform = LoginForm()

    if loginform.validate_on_submit():
        email = loginform.email.data
        password = loginform.password.data

        if User.query.filter_by(email=email).first():
            user = User.query.filter_by(email=email).first()
        else:
            flash("This email doesn't exist. Please check and try again.")
            return redirect(url_for('login'))

        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home', current_user=current_user))
        else:
            flash("Incorrect Password. Please check and try again.")
            return redirect(url_for('login'))
    return render_template("new-login.html", form=loginform)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/journal", methods=["GET", "POST"])
def show_journal():
    all_posts = GymJournal.query.all()
    print(f"All posts: {all_posts}")

    if request.method == "POST":
        if current_user.is_authenticated:
            today_entry = request.form.get('entry')
            new_entry = GymJournal(
                month=date.today().strftime("%B %Y"),  ## month format in "October 2022, 20 Thursday" - easier to call
                day=date.today().strftime("%d %A"),
                body=today_entry
            )
            db.session.add(new_entry)
            db.session.commit()
            return redirect(url_for('show_journal'))

        else:
            print("not logged in")
            flash("Register or Sign In to comment")
            return redirect(url_for('login'))

    return render_template("new-diary.html", posts=all_posts, current_user=current_user)


@app.route("/delete/<int:post_id>", methods=["POST", "GET"])
def delete_post(post_id):
    post_to_delete = GymJournal.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('show_journal'))


if __name__ == '__main__':
    app.run(debug=True)
