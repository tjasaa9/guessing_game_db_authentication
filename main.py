import random
import hashlib
import uuid
from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, db

app = Flask(__name__)
#create new tables in database
db.create_all() 

@app.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
       user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None
    
    return render_template("index.html", user=user)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    #hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    #create a secret number
    secret_number = random.randint(1,10)

    #does the user already exist?
    user = db.query(User).filter_by(email=email).first()

    if not user:
        #if it doesn't exist yet, create a User object
        user = User(name=name, email=email, secret_number=secret_number, password=hashed_password)
        user.save()

    #check if the password is incorrect
    if hashed_password != user.password:
        return "Wrong password! Try again."
    elif hashed_password == user.password:
        #create a session token for this user
        session_token = str(uuid.uuid4())

        #save a session token in a database
        user.session_token = session_token
        user.save()

        #save user's session token into a cookie
        response = make_response(redirect(url_for("index")))
        response.set_cookie("session_token", session_token, httponly=True, samesite="Strict")


        return response

@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")

    #get user from the database based on his/her email address
    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("index"))

@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))

    session_token = request.cookies.get("session_token")

    # get user from the database based on her/his email address
    user = db.query(User).filter_by(session_token=session_token).first()

    
    if guess == user.secret_number:
        message = "Correct! The secret number is {0}".format(str(guess))

        #create a new secret number
        new_secret = random.randint(1, 10)

        #update the user's secret number
        user.secret_number = new_secret
        user.save()

    elif guess > user.secret_number:
        message = "Your guess is incorrect, try something smaller."
    elif guess < user.secret_number:
        message = "Your guess is incorrect, try something bigger."

    return render_template("result.html", message=message)

@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")

    #get user from the db based on their email
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user: #if user exists
            return render_template("profile_edit.html", user=user)
        else:
            return redirect(url_for("index"))

    #if the user changes their info  
    elif request.method == "POST":
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")

        #update the user object
        user.name = name
        user.email = email

        #store changes into the database
        user.save()

        return redirect(url_for("profile"))

@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")

    #find user from the db by their email address
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user: #if user exists
            return render_template("profile_delete.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":
    #delete the user in the database
        user.delete()

        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(use_reloader=True)
