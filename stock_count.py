import csv
import requests
import json
import sys
import os

token = '2tQzNrcZpJ7vDDXgznMJzk_GaKTP5KLMlyD4v9cX'
outlets = {'MTA':'01f9c6db-e35e-11e2-a415-bc764e10976c',
'GAR':'064dce89-c73d-11e5-ec2a-c92ca32c62a3',
'JFK':'605445f3-3846-11e2-b1f5-4040782fde00',
'BAS':'f92e438b-3db4-11e2-b1f5-4040782fde00'}

#Establish Session
s = requests.Session()
s.headers.update({"User-Agent":"theharvardshop_stocktools_JS","Authorization":"Bearer %s" %token})

#Get product information
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
        return None

#Returns count of product_id in outlet as integer
def get_count(response,product_id,outlet):
    if 'inventory' not in response:
        print(response)
        print("Error, could not get product inventory")
        exit(1)
    for d in response['inventory']:
        if d['outlet_id']==outlet:
            return int(float(d['count']))

def write_csv(out_file,change_list):
    fieldnames = ['product_name', 'supply_price','old_count','new_count','dif','value_change','updated_at']
    if os.path.isfile(out_file):
        with open(out_file,'a') as f:
            writer = csv.DictWriter(f,fieldnames)
            writer.writerows(change_list)
    else:
        with open(out_file,'w') as f:
            writer = csv.DictWriter(f,fieldnames)
            writer.writeheader()
            writer.writerows(change_list)


# returns dict of "product_id":"count"
def get_inventory():
    return

def prewrite(product_id,d):
    r = s.get("https://harvardshop.vendhq.com/api/products/{}".format(product_id)).json()
    try:
        r = r['products'][0]
    except['KeyError']:
        print("Error, could not get product list")
        exit(1)
    d['old_count'] = get_count(r,product_id,outlet)
    d['product_name']=r['name']
    #if 'variant_name' in p:
    #    d['variant_name'] = p['variant_name']

def postwrite(product_id,response,d):
    if 'product' not in response:
        print("Error: {}, sku: {}".format(response['error'],sku))
        return
    response = response['product']
    d['supply_price'] = float(response['supply_price'])
    d['new_count'] = get_count(response,product_id,outlet)
    d['dif'] = d['new_count']-d['old_count']
    d['value_change'] = d['supply_price']*d['dif']
    d['updated_at'] = response['updated_at']
    changes.append(d)
    print("successfully updated {} from {} to {}".format(d['product_name'],d['old_count'],d['new_count']))

def error(str):
    print("{}, ".format("run: python3 stock_count.py filename.csv storename [outputfile.csv]"))
    print("valid storenames: 'MTA','GAR',JFK','BAS'")
    exit(1)

#begin script
if len(sys.argv) < 3:
    error("Invalid argument number")
try:
    out_file = sys.argv[1]
    outlet = outlets[sys.argv[2]]
except KeyError:
    error("Invalid outlet")

if len(sys.argv) == 3:
    while True:
        changes = []
        try:
            sku,count = list(map(int,input("Format [sku] [count]: ").split(',')))
        except ValueError:
            print("Wrong format")
            continue
        if get_id(sku) == None:
            continue
        product_id = get_id(sku)
        d = {}
        prewrite(product_id,d)
        payload = json.dumps({"id":product_id,"inventory":[{"outlet_id":outlet,"count":count}]})
        r = s.post("https://harvardshop.vendhq.com/api/products",data=payload)
        #write results to csv (new_count,dif)
        postwrite(product_id,r.json(),d)
        write_csv(out_file,changes)

if len(sys.argv) == 4:
    try:
        with open(sys.argv[3],'r',newline='') as f:
            reader = csv.reader(f)
            changes = []

            for row in reader:
                if len(row) != 2:
                    print("Error: format issue")
                    break
                row = [int(e) for e in row]
                sku, count = row
                if get_id(sku) == None:
                    continue
                product_id = get_id(sku)

                #get following information (name,product_id,sku,old_count)
                d = {}
                prewrite(product_id,d)
                payload = json.dumps({"id":product_id,"inventory":[{"outlet_id":outlet,"count":count}]})
                r = s.post("https://harvardshop.vendhq.com/api/products",data=payload)

                #write results to csv (new_count,dif)
                postwrite(product_id,r.json(),d)
            write_csv(out_file,changes)
    except FileNotFoundError:
        error('input file not found')
