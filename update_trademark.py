import requests
import sheets
import os
import csv
import sys
from datetime import date,timedelta

trademark_id = 'e52b2846-e93d-11e5-f98b-4867baceded1'
trademarkSheetsId = '1wxawuMNOiNHITD1Y_Sp97xYCqRuuWiApTLT7IpLVdjQ'

token = '2tQzNrcZpJ7vDDXgznMJzk_rj51acWDtNLT3vyQ1'
outlets = {'MTA':'01f9c6db-e35e-11e2-a415-bc764e10976c',
'GAR':'064dce89-c73d-11e5-ec2a-c92ca32c62a3',
'JFK':'605445f3-3846-11e2-b1f5-4040782fde00',
'BAS':'f92e438b-3db4-11e2-b1f5-4040782fde00'}
trash = ['Discount','Checkout Bag Charge (25 cents)','Smart Water 20 OZ.',
'Soda/Dasani','Additional Bag Charge ($1)','Tour Hahvahd Trademark Tour']

s = requests.Session()
s.headers.update({'User-Agent':'theharvardshop_stocktools_JS',"Authorization":"Bearer %s" %token})

def get_sales(start,end,outlet,customer_id):
    start = str(start) + 'T04:00:00Z'
    end = str(end) + 'T04:00:00Z'
    print(start,end)
    sales_dict = {}
    if customer_id:
        url = 'https://harvardshop.vendhq.com/api/2.0/search?date_from={}&date_to={}&order_by=date&order_direction=desc&page_size=1000&status=closed&type=sales&outlet_id={}&customer_id={}'.format(start,end,outlets[outlet],customer_id)
    else:
        url = 'https://harvardshop.vendhq.com/api/2.0/search?date_from={}&date_to={}&order_by=date&order_direction=desc&page_size=1000&status=closed&type=sales&outlet_id={}'.format(start,end,outlets[outlet])
    try:
        r = s.get(url).json()
    except:
        print(url)
        print(s.get(url))
        print("Incorrect Key")
        exit(1)
    return(r['data'])

def print_sales(start,end,outlet,csv_file='export_file.csv',customer_id=None):
    sales_dict = get_sales(start,end,outlet,customer_id)
    with open(csv_file,'w') as f:
        writer = csv.writer(f)
        writer.writerow(['name','sku','amount sold'])
        for key, value in sales_dict.items():
            try:
                name = products[key]
                if name in trash:
                    continue
                writer.writerow([name,sku_dict[key],value])
            except KeyError:
                continue

def total_price(sales_list):
    total = 0
    for sale in sales_list:
        total += sale['total_price']
    return total

if len(sys.argv) == 1:
    today = date.today()
if len(sys.argv) == 3:
    year = 2017
    month = int(sys.argv[1])
    day = int(sys.argv[2])
    today = date(year,month,day)
if len(sys.argv) == 4:
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    day = int(sys.argv[3])
    today = date(year,month,day)

tomorrow = today+timedelta(1)
jfk_total = total_price(get_sales(today,tomorrow,'JFK',trademark_id))
mta_total = total_price(get_sales(today,tomorrow,'MTA',trademark_id))
gar_total = total_price(get_sales(today,tomorrow,'GAR',trademark_id))
row = today.day+2
range_name = "J{}:L{}".format(row,row)
sheets.update(trademarkSheetsId,range_name,[[jfk_total,mta_total,gar_total]])
