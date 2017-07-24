import csv
import requests
import json
import sys
import os
# Usage : stock.py out.csv outlet [in.csv] [add]
# OR      stock.py negatives outlet

TOKEN = os.environ['token']
outlets = {'MTA':'01f9c6db-e35e-11e2-a415-bc764e10976c',
'GAR':'064dce89-c73d-11e5-ec2a-c92ca32c62a3',
'JFK':'605445f3-3846-11e2-b1f5-4040782fde00',
'BAS':'f92e438b-3db4-11e2-b1f5-4040782fde00'}
stock_file = 'product-export.csv'

#Establish Session
s = requests.Session()
s.headers.update({"User-Agent":"theharvardshop_stocktools_JS","Authorization":
    "Bearer {}".format(TOKEN)})

#Get sku, pid correspondence
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
    fieldnames = ['product_name', 'sku','product_id','supply_price','old_count'
        ,'new_count','dif','value_change','updated_at']
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

def prewrite(product_id,d,outlet):
    r = s.get("https://harvardshop.vendhq.com/api/products/{}".format(
        product_id)).json()
    try:
        r = r['products'][0]
    except:
        print("Error, could not get product list")
        print(r)
        return
    d['old_count'] = get_count(r,product_id,outlet)
    d['product_name']=r['name']

def postwrite(product_id,response,d,outlet,changes):
    if 'product' not in response:
        print("Error: {}, sku: {}".format(response['error'],sku))
        return
    response = response['product']
    d['supply_price'] = float(response['supply_price'])
    d['new_count'] = get_count(response,product_id,outlet)
    d['dif'] = d['new_count']-d['old_count']
    d['value_change'] = d['supply_price']*d['dif']
    d['updated_at'] = response['updated_at']
    d['product_id'] = product_id
    changes.append(d)
    print("successfully updated {} from {} to {}".format(d['product_name'],
        d['old_count'],d['new_count']))

def error(str):
    print("{}, ".format('run: python3 stock_count.py filename.csv storename'
        '[outputfile.csv]'))
    print("valid storenames: 'MTA','GAR',JFK','BAS'")
    exit(1)

def find_negatives(outlet_id):
    negatives = []
    r=s.get("https://harvardshop.vendhq.com/api/2.0/inventory").json()
    #Paginate through
    while True:
        if r['data'] == {}:
            print('Done')
            break
        for item in r['data']:
            if item['outlet_id'] == outlet_id and item['inventory_level'] < 0:
                d = {}
                prewrite(item['product_id'],d,outlet_id)
                try:
                    unlawful_item = {'product_name':d['product_name'],'count':
                        item['inventory_level']}
                    negatives.append(unlawful_item)
                    print(unlawful_item)
                except KeyError:
                    continue
        r=s.get("https://harvardshop.vendhq.com/api/2.0/inventory?after={}"
                .format(r['version']['max'])).json()
    return negatives


def update_inventory(product_id,outlet,count):
    return s.post("https://harvardshop.vendhq.com/api/products",data=json.dumps
        ({"id":product_id,"inventory":[{"outlet_id":outlet,"count":count}]}))

def description():
    print("Usage : stock.py out.csv outlet [in.csv] [add]")
    print("OR stock.py negatives outlet")

def cli(out_file,outlet):
    while True:
        changes = []
        try:
            sku,count = list(map(int,input("Format [sku] [count]: ")
                .split(',')))
        except ValueError:
            print("Wrong format")
            continue
        if get_id(sku) == None:
            continue
        product_id = get_id(sku)
        d = {}
        prewrite(product_id,d,outlet)
        r = update_inventory(product_id,outlet,count)
        #write results to csv (new_count,dif)
        postwrite(product_id,r.json(),d,outlet,changes)
        write_csv("logs/{}".format(out_file),changes)

def _get_outlet():
    try:
        return outlets[sys.argv[2]]
    except KeyError:
        print("Outlet does not exist")
        return 0

def update(in_file,out_file,outlet):
    try:
        with open(in_file,'r',newline='') as f:
            reader = csv.reader(f)
            changes = []

            for row in reader:
                if len(row) != 2:
                    print("Error: format issue with input file")
                    break
                row = [int(e) for e in row]
                sku, count = row
                if get_id(sku) == None:
                    continue
                product_id = get_id(sku)

                #Gets following information (name,product_id,sku,old_count)
                d = {"sku":sku}
                prewrite(product_id,d,outlet)
                if len(sys.argv) == 5:
                    count = count + d['old_count']
                r = update_inventory(product_id,outlet,count)

                #Write results to csv (new_count,dif)
                postwrite(product_id,r.json(),d,outlet)
            write_csv("logs/{}".format(out_file),changes)
    except FileNotFoundError:
        error('input file not found')

def main():
    args = len(sys.argv)
    if args == 1:
        return description()
    elif args == 2:
        return description()
    elif args == 3:
        out_file = sys.argv[1]
        outlet = _get_outlet()
        return cli(out_file,outlet)
    else:
        out_file = argv[1]
        outlet = _get_outlet()
        return update(out_file,outlet,in_file)
    exit(0)

#if sys.argv[1] == 'negatives':
#    outlet = sys.argv[2]
#    product_list = find_negatives(outlets[outlet])
#    with open(sys.argv[3],'w') as f:
#        writer = csv.writer(f)
#        writer.writerow(['product name','quantity',outlet])
#        for d in product_list:
#            writer.writerow([d['product_name'],d['count']])
#    print('Sucessful Write')
#    exit(0)

if __name__ == "__main__":
    main()
