import csv
import requests
import json

token = '2tQzNrcZpJ7vDDXgznMJzk_Cjr7L8eEIURUw5Lm6'
MTA = '01f9c6db-e35e-11e2-a415-bc764e10976c'
GAR = '064dce89-c73d-11e5-ec2a-c92ca32c62a3'
JFK = '605445f3-3846-11e2-b1f5-4040782fde00'
BAS = 'f92e438b-3db4-11e2-b1f5-4040782fde00'

#Modify this part
outlet = MTA
stock_file = "product-export.csv"

#read products into dict
with open(stock_file,mode='r',encoding='latin-1') as fp:
    reader = csv.reader(fp)
    products = {}
    for row in reader:
        try:
            products[int(row[2])]=row[0]
        except ValueError:
            continue

def get_id(sku):
    try:
        return products[sku]
    except KeyError:
        print("Key Error for sku {}".format(sku))

with open('stock_count.csv',newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) != 2:
            print("Error: format issue")
            break
        row = [int(e) for e in row]
        sku, count = row
        payload = json.dumps({"id":get_id(sku),"inventory":[{"outlet_id":outlet,"count":count}]})
        r = requests.post("https://harvardshop.vendhq.com/api/products",data=payload,headers={"Authorization":"Bearer %s" %token})
        if 'status' in r.json():
            print("Error: {}, sku: {}".format(r.json()['error'],sku))
        else:
            print("successfully updated sku {}".format(sku))
