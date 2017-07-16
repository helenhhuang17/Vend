import os
import re
import requests
import csv
from flask import Flask, jsonify, render_template, request, url_for, redirect
from flask_jsglue import JSGlue
from .vend import Vend

#read products into dict
with open("product-export.csv",mode='r',encoding='latin-1') as fp:
    reader = csv.reader(fp)
    products = {row[0]:row[6] for row in reader}

# configure application
app = Flask(__name__)
JSGlue(app)


# global client secret key
client_secret = 'j5PM7viAPHCZ6DMCIH4NLFvQeCiwVf4H'
client_id = 'vQ7l7OTmVg8OBET6vwdSXoCDOmvvJ05F'
token = '2tQzNrcZpJ7vDDXgznMJzk_Cjr7L8eEIURUw5Lm6'

vend = Vend('harvardshop',token)

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
    if request.args.get('code',''):
        code = request.args.get('code','')
        domain_prefix = request.args.get('domain_prefix','')
        d = {"code":code,"client_id":client_id,"client_secret":client_secret,
        "grant_type":"authorization_code","redirect_uri":"http://127.0.0.1:5000"}
        r = requests.post("https://{}.vendhq.com/api/1.0/token".format(domain_prefix),d)
        global token
        token = r.json()["access_token"]
        print(token)
    sales = vend.get_sales()
    for sale in sales['data']:
        for line in sale['line_items']:
            try:
                line['product_name']=products[line['product_id']]
            except KeyError:
                line['product_name']='no name'
            print(line['product_name'])
    return render_template("index.html", sales = sales)

@app.route("/login")
def login():
    return redirect("https://secure.vendhq.com/connect?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&state=None".format(client_id=client_id,redirect_uri="http://127.0.0.1:5000"))

@app.route("/inventory")
def inventory():
    url = "https://harvardshop.vendhq.com/api/2.0/inventory"
    response = requests.get(url,headers={"Authorization":"Bearer %s" %token})
    print("{}".format(response.text))
    return render_template("inventory.html",r=response.json()['data'])
