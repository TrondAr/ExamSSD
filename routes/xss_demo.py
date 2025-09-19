from flask import Blueprint, render_template_string, request

xss_bp = Blueprint("xss_demo", __name__, url_prefix="/xss")

@xss_bp.get("/echo")
def echo():    
    q = request.args.get("q", "")
    return render_template_string("<p>You said: {{ q }}</p>", q=q)