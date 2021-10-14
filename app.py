import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env


app = Flask(__name__)
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def get_activities():
    activities = list(mongo.db.activities.find())
    return render_template("activities.html", activities=activities)


@app.route("/add/activity", methods=["GET", "POST"])
def add_activity():
    if request.method == "POST":
        activity = {
            "month": request.form.get("month"),
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


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
