# routes/my_dashboard.py
from flask import Blueprint, render_template, session, redirect, url_for
from models.database import get_user_history, get_user_stats, get_user_by_id

my_dashboard_bp = Blueprint("my_dashboard", __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login") + "?next=/my-dashboard")
        return f(*args, **kwargs)
    return decorated


@my_dashboard_bp.route("/my-dashboard")
@login_required
def my_dashboard():
    user_id = session["user_id"]
    user    = get_user_by_id(user_id)
    history = get_user_history(user_id, limit=50)
    stats   = get_user_stats(user_id)
    return render_template("my_dashboard.html",
                           user=user, history=history, stats=stats)
