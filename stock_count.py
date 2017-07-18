import csv
import requests
import json
import sys

token = '2tQzNrcZpJ7vDDXgznMJzk_PSkKmshstsagRVsOo'
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
        return None

#returns count of product_id in outlet as integer
def get_count(product_id,outlet):
    p = requests.get("https://harvardshop.vendhq.com/api/2.0/products/{}/inventory".format(product_id),headers={"Authorization":"Bearer %s" %token}).json()
    if 'data' not in p:
        print(p)
        print("Error, could not get product inventory")
        exit(1)
    for d in p['data']:
        if d['outlet_id']==outlet:
            return int(d['current_amount']) #what is the dif between this and inventory_level?

def write_csv(out_file,change_list):

    with open(out_file,'w') as f2:
        fieldnames = ['product_name', 'supply_price','old_count','new_count','dif','value_change']
        writer = csv.DictWriter(f2,fieldnames)
        writer.writeheader()
        for c in change_list:
            writer.writerow(c)
# returns dict of "product_id":"count"
def get_inventory():
    return

def prewrite(product_id,d):
    p = requests.get("https://harvardshop.vendhq.com/api/products/{}".format(product_id),headers={"Authorization":"Bearer %s" %token}).json()
    if 'products' not in p:
        print(p)
        print("Error, could not get product list")
        exit(1)
    p = p['products'][0]
    d['old_count'] = get_count(product_id,outlet)
    d['product_name']=p['name']


    #if 'variant_name' in p:
    #    d['variant_name'] = p['variant_name']



def postwrite(product_id,response,d):
    if 'product' not in response:
        print("Error: {}, sku: {}".format(response['error'],sku))
        return
    response = response['product']
    d['supply_price'] = response['supply_price']
    d['new_count'] = get_count(product_id,outlet)
    d['dif'] = d['new_count']-d['old_count']
    d['value_change'] = d['supply_price']*d['dif']
    changes.append(d)
    print("successfully updated {} from {} to {}".format(d['product_name'],d['old_count'],d['new_count']))

#begin script
if len(sys.argv) != 4:
    print('run: python3 stock_count.py [filename.csv] [storename] [outputfile.csv]')
    exit(1)
try:
    with open(sys.argv[1],newline='') as f:
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
            r = requests.post("https://harvardshop.vendhq.com/api/products",data=payload,headers={"Authorization":"Bearer %s" %token})

            #write results to csv (new_count,dif)
            postwrite(product_id,r.json(),d)
        write_csv(sys.argv[3],changes)
except FileNotFoundError:
    print('File not found')
    exit(1)
