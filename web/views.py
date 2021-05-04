from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.helpers import make_response
from flask_login import current_user
from flask_login.utils import login_required
from .models import Pastebin
from .util.pastebin_util import PastebinUtil
from . import db

views = Blueprint("views", __name__)

@views.route("/", methods=["GET", "POST"])
def home():
   if request.method == "POST":
      title = request.form.get("title")
      pastebin = request.form.get("pastebin")
      private = request.form.get("private")
      password = request.form.get("password")

      if check_pastebin(title, pastebin):
         new_pastebin = Pastebin(title=title, content=pastebin, user_id=None if current_user.is_anonymous else current_user.id)  

      db.session.add(new_pastebin)
      db.session.commit()
      new_pastebin.link = PastebinUtil.base36_encode(new_pastebin.id)
      response = make_response(redirect(url_for("views.pastebins", link=new_pastebin.link)))
      if private == "True":
         new_pastebin.password = password
         response.set_cookie(new_pastebin.link, new_pastebin.password)   
      db.session.commit()

      flash("Pastebin added!", category="success")
      return response
         
   return render_template("home.html", user=current_user)

@views.route("/<link>", methods=["GET", "POST"])
def pastebins(link: str):
   if request.method == "GET":
      pastebin = Pastebin.query.filter_by(link=link).first()
      password_cookie = request.cookies.get(link)
      if pastebin:
         if pastebin.password == None or password_cookie == pastebin.password:
            return render_template("pastebin.html", user=current_user, pastebin=pastebin)
         else:
            return render_template("pastebin.html", user=current_user, pastebin=pastebin, password=pastebin.password)
      else:
         flash("Can't find pastebin.", category="error")
         return redirect(url_for("views.home"))
   
   if request.method == "POST":
      pastebin = Pastebin.query.filter_by(link=link).first()
      password = request.form.get("password")
      response = make_response(render_template("pastebin.html", user=current_user, pastebin=pastebin))

      if password == pastebin.password:
         response.set_cookie(link, pastebin.password)
         return response
      else:
         flash("Password is incorrect!", category="error")
         return redirect(url_for("views.pastebins", link=link))



@views.route("/user")
@login_required
def user():
   return render_template("user.html", user=current_user)

def check_pastebin(title: str, pastebin: str):
   if len(title) < 3:
      flash("Title must be at least 3 characters long.", category="error")
   elif len(title) > 150:
      flash("Title cannot exceed 150 characters limit.", category="error")
   elif len(pastebin) < 1:
      flash("Your pastebin must be at least 1 character long.", category="error")
   elif len(pastebin) > 6000000:
      flash("Your pastebin cannot exceed 6000000 characters limit.", category="error")
   else:
      return True
