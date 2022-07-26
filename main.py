from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from typing import Callable
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_key"
Bootstrap(app)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Boolean: Callable
    Integer: Callable


db = MySQLAlchemy(app)


##Library TABLE Configuration
class GymLibrary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String(), unique=True, nullable=False)

    def to_dict(self):
        dictionary = {}

        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)

        return dictionary

db.create_all()


class GymSearch(FlaskForm):
    exc = StringField("Search exercise here", render_kw={"placeholder": "Search exercise here", 'style': 'width: 45ch, height: 4ch '})
    submit = SubmitField("Search")


# gym_list = gym_list[0]

@app.route("/", methods=["GET", "POST"])
def home():

    gymdata = GymLibrary.query.all()

    # tasks = db.session.query(Task).all()
    # gymdata = [(task.to_dict()) for task in tasks]
    form = GymSearch()
    if request.method == "POST":
        if form.validate_on_submit():
            exercise = form.exc.data

            headers = {
                "X-RapidAPI-Key": "bb8f721820msh41917aa6a4592a7p1466e2jsn11d3b1b25ada",
                "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
            }
            url = f"https://exercisedb.p.rapidapi.com/exercises/name/{exercise}"

            response = requests.request("GET", url, headers=headers)

            ex_list = response.json()
            print(ex_list)
            # gym_list.append(ex_list)


            # new_post = GymLibrary(
            #     exercise=ex_list
            # )
            #
            # db.session.add(new_post)
            # db.session.commit()
            return render_template("index.html", data=gymdata, form=form, exercise_list=ex_list)
    # print(f"this is gymlist {gym_list}")

    # return render_template("index.html", tasks=task_list, form=form)
    return render_template("index.html", data=gymdata, form=form)







# @app.route("/add_book", methods=["GET", "POST"])
# def add_book():
#     form = BookForm()
#     if form.validate_on_submit():
#         new_book = Library(
#             name=form.name.data,
#             img_url=form.img.data,
#             synopsis=form.synop.data,
#             author=form.auth.data,
#             rating=form.rating.data
#         )
#         db.session.add(new_book)
#         db.session.commit()
#
#         return redirect(url_for('home'))
#     return render_template("add_book.html", form=form)


# @app.route("/delete/<int:post_id>", methods=["POST", "GET"])
# def delete_post(post_id):
#     post_to_delete = Library.query.get(post_id)
#     db.session.delete(post_to_delete)
#     db.session.commit()
#     return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)





