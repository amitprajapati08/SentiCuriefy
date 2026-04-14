from flask import Blueprint, render_template
from models.database import get_dashboard_stats, get_community_stats

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    stats     = get_dashboard_stats()
    community = get_community_stats()
    return render_template("dashboard.html", stats=stats, community=community)
