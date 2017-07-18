import os
import re
import requests
import csv
from flask import Flask, jsonify, render_template, request, url_for, redirect, Session
from flask_jsglue import JSGlue
from .vend import Vend

#read products into dict
with open("product-export.csv",mode='r',encoding='latin-1') as fp:
    reader = csv.reader(fp)
    products = {row[0]:row[6] for row in reader}

# configure application
app = Flask(__name__)
JSGlue(app)
s = requests.Session()
s.headers.update({'User-Agent':'theharvardshop_stocktools_JS'})

# global client secret key
client_secret = 'j5PM7viAPHCZ6DMCIH4NLFvQeCiwVf4H'
client_id = 'vQ7l7OTmVg8OBET6vwdSXoCDOmvvJ05F'
token = '2tQzNrcZpJ7vDDXgznMJzk_GaKTP5KLMlyD4v9cX'

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
    global token
    if request.args.get('code',''):
        code = request.args.get('code','')
        domain_prefix = request.args.get('domain_prefix','')
        payload = {"code":code,"client_id":client_id,"client_secret":client_secret,
        "grant_type":"authorization_code","redirect_uri":"http://127.0.0.1:5000"}
        r = s.post("https://{}.vendhq.com/api/1.0/token".format(domain_prefix),payload)
        token = r.json()["access_token"]
        print(token)
    try:
        vend = Vend('harvardshop',token)
        sales = vend.get_sales()
        outlets = {outlet['id']:outlet['name'] for outlet in vend.get_outlets()['data']}
    except:
        return redirect("https://secure.vendhq.com/connect?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&state=None".format(client_id=client_id,redirect_uri="http://127.0.0.1:5000"))
    for sale in sales['data']:
        sale['outlet']=outlets[sale['outlet_id']]
        for line in sale['line_items']:
            try:
                line['product_name']=products[line['product_id']]
            except KeyError:
                sale['line_items'].remove(line)
    return render_template("index.html", sales = sales)

@app.route("/login")
def login():
    return redirect("https://secure.vendhq.com/connect?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&state=None".format(client_id=client_id,redirect_uri="http://127.0.0.1:5000"))

@app.route("/inventory")
def inventory():
    url = "https://harvardshop.vendhq.com/api/2.0/inventory"
    response = s.get(url)
    return render_template("inventory.html",r=response.json()['data'])
