# routes/main.py
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


# NOTE: /predict is intentionally NOT here.
# It is registered by analysis_bp in routes/analysis.py (GET + POST).
# Having it in both blueprints caused a "View function mapping is overwriting" error.


@main_bp.route('/process')
def process():
    return render_template('process.html')
