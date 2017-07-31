import requests
import sheets
import os
import csv
import sys
import vend
import argparse
from datetime import date, timedelta, datetime

ticket_id = '3711220b-ffdc-11e2-a415-bc764e10976c'
trademark_id = 'e52b2846-e93d-11e5-f98b-4867baceded1'
trademarkSheetsId = '1uIw28MRuF8pEukgpUrbXXyFLGkXc16PRar8aPt8xybg'
token = os.environ['token']

outlets = {'MTA':'01f9c6db-e35e-11e2-a415-bc764e10976c',
'GAR':'064dce89-c73d-11e5-ec2a-c92ca32c62a3',
'JFK':'605445f3-3846-11e2-b1f5-4040782fde00',
'BAS':'f92e438b-3db4-11e2-b1f5-4040782fde00'}
trash = ['Discount','Checkout Bag Charge (25 cents)','Smart Water 20 OZ.',
'Soda/Dasani','Additional Bag Charge ($1)','Tour Hahvahd Trademark Tour']

s = requests.Session()
s.headers.update({'User-Agent':'theharvardshop_trademark',
"Authorization":"Bearer %s" %token})

def get_sales(start,end,outlet,customer_id=trademark_id):
    start = str(start) + 'T04:00:00Z'
    end = str(end) + 'T04:00:00Z'
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

#Returns Price of total product
def filter_sales(sales,product_id):
    total = 0
    for sale in sales:
        for item in sale['line_items']:
            if item['product_id'] == product_id:
                total += item['price_total']
    return total

def main():
    parser = argparse.ArgumentParser(description='Update Sales')
    parser.add_argument("-d", "--date", help="MM/DD/YYYY")
    args = parser.parse_args()

    if args.date:
        try:
            today = datetime.strptime(args.date, "%m/%d/%Y").date()
        except ValueError:
            print("Error: format date as MM/DD/YYYY")
            exit(1)
    else:
        today = date.today()
    tomorrow = today+timedelta(1)

    JFK_sales = get_sales(today,tomorrow,'JFK',trademark_id)
    MTA_sales = get_sales(today,tomorrow,'MTA',trademark_id)
    GAR_sales = get_sales(today,tomorrow,'GAR',trademark_id)
    jfk_total = total_price(JFK_sales)
    mta_total = total_price(MTA_sales)
    gar_total = total_price(GAR_sales)

    ticket_total = filter_sales(JFK_sales+MTA_sales+GAR_sales,ticket_id)

    row = today.day + 2
    range_name = "J{}:L{}".format(row,row)
    sheets.update(trademarkSheetsId,range_name,[[jfk_total,mta_total,gar_total]])
    sheets.update(trademarkSheetsId,"O{}".format(row),[[ticket_total]])

if __name__ == "__main__":
    main()
