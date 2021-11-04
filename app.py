import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from flask_login import current_user
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)



@app.route("/")
def get_activities():
    now = datetime.now()
    activities = list(mongo.db.activities.find({'month': now.strftime('%B')}))
    print(activities)
    return render_template("activities.html", activities=activities)


@app.route("/filter", methods=["GET", "POST"])
def filter_activities():
    month = request.form.get('month')
    activities = list(mongo.db.activities.find({'month': month}))
    print(activities)
    return render_template("activities.html", activities=activities)


@app.route("/register/user", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("pages/register-user.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            # return redirect(url_for("login")
    return render_template("pages/login-user.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if session["user"]:
        return render_template("pages/profile-user.html", username=username)
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add/activity", methods=["GET", "POST"])
def add_activity():
    if request.method == "POST":
        activity = {
            "month": request.values.get("month"),
            "theme": request.form.get("theme"),
            "letter_of_week": request.form.get("letter-of-week"),
            "book": request.form.get("book"),
            "book_description": request.form.get("book_description"),
            "craft": request.form.get("craft"),
            "craft_description": request.form.get("craft_description"),
            "game": request.form.get("game"),
            "game_description": request.form.get("game_description"),
            "watercolour": request.form.get("watercolour"),
            "watercolour_description": request.form.get("watercolour_description")          
        }
        mongo.db.activities.insert_one(activity)
        flash("Activity Successfully Added")
        return redirect(url_for("get_activities"))
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("pages/add-activity.html", categories=categories)


@app.route("/edit/activity/<activity_id>", methods=["GET", "POST"])
def edit_activity(activity_id):
    if request.method == "POST":
        submit = {
            "month": request.values.get("month"),
            "theme": request.form.get("theme"),
            "letter_of_week": request.form.get("letter-of-week"),
            "book": request.form.get("book"),
            "book_description": request.form.get("book_description"),
            "craft": request.form.get("craft"),
            "craft_description": request.form.get("craft_description"),
            "game": request.form.get("game"),
            "game_description": request.form.get("game_description"),
            "watercolour": request.form.get("watercolour"),
            "watercolour_description": request.form.get("watercolour_description")          
        }
        mongo.db.activities.update({"_id": ObjectId(activity_id)}, submit)
        flash("Activity Successfully Updated")
    activity = mongo.db.activities.find_one({"_id": ObjectId(activity_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("pages/edit-activity.html", activity=activity, categories=categories)


@app.route("/delete/<activity_id>")
def delete_activity(activity_id):
    mongo.db.activities.remove({"_id": ObjectId(activity_id)})
    flash("Activity Successfully Deleted")
    return redirect(url_for("get_activities"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
