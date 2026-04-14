# app.py
from flask import Flask
from config import Config
from models.database import init_db
from routes.main import main_bp
from routes.product import product_bp
from routes.analysis import analysis_bp
from routes.share import share_bp
from routes.dashboard import dashboard_bp
from routes.auth import auth_bp
from routes.my_dashboard import my_dashboard_bp

try:
    from scripts.generate_visualizations import generate_plots
    _has_plots = True
except Exception:
    _has_plots = False


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY

    init_db()

    if _has_plots:
        try:
            generate_plots()
        except Exception as e:
            print(f"[startup] plot generation skipped → {e}")

    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(share_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(my_dashboard_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5002, threaded=True)
    