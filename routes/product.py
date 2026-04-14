from flask import Blueprint, render_template, request
from services.product_service import analyze_product_reviews

product_bp = Blueprint("product", __name__)


@product_bp.route("/product", methods=["GET", "POST"])
def product():
    result = None
    error  = None
    reviews_text = ""

    if request.method == "POST":
        reviews_text = request.form.get("reviews", "").strip()
        if not reviews_text:
            error = "Please paste at least one review."
        else:
            result = analyze_product_reviews(reviews_text)
            if "error" in result:
                error  = result["error"]
                result = None

    return render_template("product.html",
                           result=result,
                           error=error,
                           reviews_text=reviews_text)