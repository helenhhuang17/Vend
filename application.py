import os
import re
import requests
from flask import Flask, jsonify, render_template, request, url_for, redirect
from flask_jsglue import JSGlue

# configure application
app = Flask(__name__)
JSGlue(app)

# global client secret key
client_secret = ''
client_id = 'vQ7l7OTmVg8OBET6vwdSXoCDOmvvJ05F'

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

@app.route("/")
def index():
    if not os.environ.get("API_KEY"):
        raise RuntimeError("API_KEY not set")
    return render_template("index.html", client_secret=os.environ.get("client_secret"))

@app.route("/login")
def login():
    return redirect("https://secure.vendhq.com/connect?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&state=None".format(client_id=os.environ.get("CLIENT_ID"),redirect_uri="http://127.0.0.1:5000/login_done"))

@app.route('/login_done')
def request_token():
    client_secret=os.environ.get("client_secret")
    code = request.args.get('code','')
    domain_prefix = request.args.get('domain_prefix','')
    d = {"code":code,"client_id":client_id,"client_secret":client_secret,
    "grant_type":"authorization_code","redirect_uri":"http://127.0.0.1:5000"}
    print(d)
    r = requests.post("https://{}.vendhq.com/api/1.0/token".format(domain_prefix),d)
    return "{}".format(r.json())
