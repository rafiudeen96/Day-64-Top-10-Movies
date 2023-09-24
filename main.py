from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField,IntegerField,URLField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movie_database.db"
Bootstrap5(app)

db = SQLAlchemy()
db.init_app(app)

#--------------------------------------------------------The Movies Table -----------------------------------------------------#

class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String,unique=True,nullable=False)
    year = db.Column(db.Integer,nullable=False)
    description = db.Column(db.String,nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer,unique=False)
    review = db.Column(db.String)
    img_url = db.Column(db.String,nullable=False)

# ---------------------------------------------------------- Edit Form (Rating and Review) -------------------------------------#

class edit_form(FlaskForm):
    rating = FloatField("Rating")
    review = StringField("Review")
    submit = SubmitField("Submit")

# ----------------------------------------------------------- Movie Add Form --------------------------------------------------#
class search_movie_form(FlaskForm):
    title = StringField("Title",validators=[DataRequired()])
    # year = IntegerField("Year",validators=[DataRequired()])
    # description = StringField("Description",validators=[DataRequired()])
    # rating = FloatField("Rating",validators=[DataRequired()])
    # ranking = IntegerField("Ranking",validators=[DataRequired()])
    # review = StringField("Review",validators=[DataRequired()])
    # img_url = URLField("Image URL",validators=[DataRequired()])
    submit = SubmitField("Submit")


def func_ranking():
    all_movies = db.session.query(Movie).all()
    for current_movie in all_movies:
        ranking = 1
        print(f"movie title - {current_movie.title}")
        for next_movie in all_movies:
            if current_movie.rating >= next_movie.rating:
                pass
            else:
                print("Ranking increased")
                if ranking == 10:
                    current_movie.ranking = ranking
                    db.session.commit()
                    break
                else:
                    ranking+=1

        current_movie.ranking = ranking
        print(f"{current_movie.title}-{current_movie.ranking}")
        db.session.commit()


@app.route("/",methods=["GET","POST"])
def home():
    func_ranking()
    all_movies = db.session.execute(db.select(Movie).order_by(Movie.ranking.desc())).scalars()
    return render_template("index.html",all_movies=all_movies)

@app.route("/edit<int:id>",methods=["GET","POST"])
def edit(id):
    form = edit_form()
    if request.method == "POST":
        if form.validate_on_submit():
            review = form.review.data
            rating = form.rating.data
            if review != "":
                movie = db.session.execute(db.select(Movie).filter_by(id=id)).scalar_one()
                movie.review = review
            if rating != None:
                movie = db.session.execute(db.select(Movie).filter_by(id=id)).scalar_one()
                movie.rating = rating
            db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html",form=form,id=id)

@app.route("/delete<int:id>")
def delete(id):
    with app.app_context():
        book_to_delete = db.session.execute(db.select(Movie).filter_by(id=id)).scalar_one()
        db.session.delete(book_to_delete)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/search',methods=["GET","POST"])
def search():
    form = search_movie_form()
    if request.method == "POST":
        # if form.validate_on_submit():
            title = form.title.data
            # year = form.year.data
            # description = form.description.data
            # rating = form.rating.data
            # ranking = form.ranking.data
            # review = form.review.data
            # img_url = form.img_url.data
            # movie_to_add = Movie(title=title,year=year,description=description,rating=rating,ranking=ranking,
            #                      review=review,img_url=img_url)
            # db.session.add(movie_to_add)
            # db.session.commit()
            parameter = {
                "api_key": "c662518df672588288dece3f0f1a419a",
                "query": {title}
            }
            response = requests.get("https://api.themoviedb.org/3/search/movie", params=parameter)
            all_movies = response.json()["results"]
            print(all_movies)

            return render_template("select.html",all_movies=all_movies,title=title)
    return render_template("add.html",form=form)

@app.route("/add/<int:id>/<title>",methods=["GET","POST"])
def add(id,title):
    parameter = {
        "api_key":"c662518df672588288dece3f0f1a419a",
        "query":{title}
    }
    all_movies = requests.get("https://api.themoviedb.org/3/search/movie",params=parameter).json()["results"]

    for movie in all_movies:
        if movie["id"] == id:
            name = movie["original_title"]
            year = movie["release_date"].split("-")[0]
            desc = movie["overview"]
            img_url =f'https://image.tmdb.org/t/p/w500{movie["poster_path"]}'
    add_new_movie = Movie(title=name,year=year,description=desc,img_url=img_url)
    with app.app_context():
        db.session.add(add_new_movie)
        db.session.commit()
    movie_id = db.session.execute(db.select(Movie).filter_by(title=name)).scalar_one().id
    return redirect(url_for("edit",id=movie_id))




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # parameter = {
    #     "api_key": "c662518df672588288dece3f0f1a419a",
    #     "query": "inside out"
    # }
    # # headers={
    # #     "connection":"keep-alive"
    # # }
    # response = requests.get("https://api.themoviedb.org/3/search/movie", params=parameter)
    # all_movies = response.json()["results"]
    # print(all_movies)
    app.run(debug=True)

