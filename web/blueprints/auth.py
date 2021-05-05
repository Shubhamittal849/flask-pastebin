from flask import Blueprint, render_template, request, flash, redirect, url_for
from web.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from web import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)

#Login view
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            #If user with given username exists and passwords are correct Log him In
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Username doesn't exist.", category="error")
    
    return render_template("login.html", user=current_user)

#Sign up view
@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        #If user is valid add it to database
        if check_user(username, email, password1, password2):
            new_user = User(username=username, email=email, password=generate_password_hash(password1, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account successfully created!", category="success")

            return redirect(url_for("views.home"))  

    return render_template("sign_up.html", user=current_user)

#Log out view
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

#Validate user
def check_user(username: str, email: str, password1: str, password2: str):
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        flash("User already exists.", category="error")
    elif len(email) < 4:
        flash("Email must be greater than 3 characters.", category="error")
    elif len(password1) < 5:
        flash("Password must be at least 5 characters long.", category="error")
    elif len(password1) > 20:
        flash("Password cannot be longer than 20 characters.", category="error")
    elif password1 != password2:
        flash("Passwords are not the same.", category="error")
    else:
        return True
