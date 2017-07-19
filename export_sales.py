import csv
import requests
import json
import sys
import os

token = os.environ['token']
outlets = {'MTA':'01f9c6db-e35e-11e2-a415-bc764e10976c',
'GAR':'064dce89-c73d-11e5-ec2a-c92ca32c62a3',
'JFK':'605445f3-3846-11e2-b1f5-4040782fde00',
'BAS':'f92e438b-3db4-11e2-b1f5-4040782fde00'}

s = requests.Session()
s.headers.update({'User-Agent':'theharvardshop_stocktools_JS',"Authorization":"Bearer %s" %token})

products = {}
r=s.get("https://harvardshop.vendhq.com/api/2.0/products").json()
while True:
    if r['data'] == []:
        break
    for item in r['data']:
        products[item['id']]=item['variant_name']
    r=s.get("https://harvardshop.vendhq.com/api/2.0/products?after={}".format(r['version']['max'])).json()

def cleanup(product_dict):
    trash_keys = ['Discount','Checkout Bag Charge (25 cents)','Smart Water 20 OZ.',
    'Soda/Dasani','Additional Bag Charge ($1)']
    for key in trash_keys:
        if key in product_dict:
            del product_dict[key]

def print_sales(start,end,outlet,csv_file='export_file.csv'):
    start = str(start) + 'T04:00:00Z'
    end = str(end) + 'T04:00:00Z'
    print(start,end)
    sales_dict = {}
    url = 'https://harvardshop.vendhq.com/api/2.0/search?date_from={}&'
        'date_to={}&order_by=date&order_direction=desc&page_size=1000&status='
        'closed&type=sales&outlet_id={}'.format(start,end,outlets[outlet])
    try:
        r = s.get(url).json()
    except:
        print(s.get(url))
        print("Incorrect Key")
        exit(1)
    for sale in r['data']:
        for item in sale['line_items']:
            try:
                sales_dict[products[item['product_id']]]+=1
            except:
                try:
                    sales_dict[products[item['product_id']]]=1
                except:
                    print('error')
                    continue
    cleanup(sales_dict)
    print(len(sales_dict))
    with open(csv_file,'w') as f:
        writer = csv.writer(f)
        writer.writerow(['name','amount sold'])
        for key, value in sales_dict.items():
            writer.writerow([key,value])
def main():
    try:
        outlet = sys.argv[1]
        csv_file = sys.argv[2]
        date1 = sys.argv[3]
        date2 = sys.argv[4]
    except IndexError:
        print("Format: python3 outlet outfile date1 date2 (yyyy-mm-dd)")

    print_sales('{}'.format(date1),'{}'.format(date2),outlet,csv_file)

if __name__ == "__main__":
    main()
