import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from flask_login import current_user
from flask_security import (Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required)
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
def home():

    """
    Will render the home page
    """

    return render_template("pages/home.html")


@app.route("/activities")
def get_activities():
    """
    Will display activities for the current month
    """
    now = datetime.now()
    activities = list(mongo.db.activities.find({'month': now.strftime('%B')}))
    return render_template("pages/activities.html", activities=activities)


@app.route("/filter", methods=["GET", "POST"])
def filter_activities():
    """
    Will filter activities based on month selected by user
    """
    month = request.form.get('month')
    activities = list(mongo.db.activities.find({'month': month}))
    return render_template("pages/activities.html", activities=activities)


@app.route("/register/user", methods=["GET", "POST"])
def register():
    """
    Will check if user exists if not
    register user in the database
    """
    if request.method == "POST":
        
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

        
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("pages/register-user.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Will check if user exists and will run validations
    for usernames and passwords
    """
    if request.method == "POST":
        
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            
            flash("Incorrect Username and/or Password")
            
    return render_template("pages/login-user.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    """
    Display session username from database
    """
    
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if session["user"]:
        return render_template("pages/profile-user.html", username=username)
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """
    Remove user from session cookie
    """
    
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add/activity", methods=["GET", "POST"])
def add_activity():
    """
    Allows user to add activities from form to the database
    """
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
            "watercolour_description": request.form.get("watercolour_description"),
            "date": request.form.get("date"),
            "date_description": request.form.get("date_description")
        }
        mongo.db.activities.insert_one(activity)
        flash("Activity Successfully Added")
        return redirect(url_for("get_activities"))
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("pages/add-activity.html", categories=categories)


@app.route("/edit/activity/<activity_id>", methods=["GET", "POST"])
def edit_activity(activity_id):
    """
    Allows user to edit activities and update the database
    """
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
            "watercolour_description": request.form.get("watercolour_description"),
            "date": request.form.get("date"),
            "date_description": request.form.get("date_description")
        }
        mongo.db.activities.update({"_id": ObjectId(activity_id)}, submit)
        flash("{} Activity Successfully Updated".format(request.form.get("theme")))
        return redirect(url_for("get_activities"))
    activity = mongo.db.activities.find_one({"_id": ObjectId(activity_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("pages/edit-activity.html", activity=activity, categories=categories)


@app.route("/delete/<activity_id>")
def delete_activity(activity_id):
    """
    Deletes activities from the database
    """
    mongo.db.activities.remove({"_id": ObjectId(activity_id)})
    flash("Activity Successfully Deleted")
    return redirect(url_for("get_activities"))


"""
Displays error pages
"""


@app.errorhandler(404)
def page_not_found(e):
    return render_template("pages/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("pages/500.html"), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=os.environ.get("DEBUG"))
