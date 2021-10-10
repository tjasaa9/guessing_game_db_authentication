import random
import hashlib
from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, db
import uuid

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

@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))

    session_token = request.cookies.get("session_token")

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

if __name__ == "__main__":
    app.run(use_reloader=True)
