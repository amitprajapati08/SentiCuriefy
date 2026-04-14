# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import create_user, verify_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("my_dashboard.my_dashboard"))

    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm", "")

        if not all([name, email, password, confirm]):
            return render_template("signup.html", error="All fields are required.")
        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters.", name=name, email=email)
        if password != confirm:
            return render_template("signup.html", error="Passwords do not match.", name=name, email=email)

        ok, msg = create_user(name, email, password)
        if ok:
            return redirect(url_for("auth.login") + "?registered=1")
        else:
            return render_template("signup.html", error=msg, name=name, email=email)

    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("my_dashboard.my_dashboard"))

    registered = request.args.get("registered")

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = verify_user(email, password)
        if user:
            session["user_id"]   = user["id"]
            session["user_name"] = user["name"]
            session.permanent    = True
            next_page = request.args.get("next", url_for("my_dashboard.my_dashboard"))
            return redirect(next_page)
        else:
            return render_template("login.html", error="Invalid email or password.", email=email)

    return render_template("login.html", registered=registered)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
