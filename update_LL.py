import update
import os
import requests
import sys
from datetime import date, datetime, timedelta, time
import sheets
import vend

LL_vend_ID = 'e52b2846-e93d-11e5-f98b-4867acedc6be'
LL_sheets_ID = '1PHwnRbhq4F4Q4I1zYGWsUTMr-oHmKOnYczsdl7zjjyQ'
sheet_ID = 1964826995

TOKEN = os.environ['token']
outlets = {'MTA':'01f9c6db-e35e-11e2-a415-bc764e10976c',
'GAR':'064dce89-c73d-11e5-ec2a-c92ca32c62a3',
'JFK':'605445f3-3846-11e2-b1f5-4040782fde00',
'BAS':'f92e438b-3db4-11e2-b1f5-4040782fde00'}

s = requests.Session()
s.headers.update({'User-Agent':'theharvardshop_LL',"Authorization":"Bearer {}".format(TOKEN)})


def main():
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
    sales = update.get_sales(today,tomorrow,'MTA',LL_vend_ID)[::-1] #Reversed
    tours = []
    sale_total = 0
    last_sale_time = vend.convert_date(sales[0]['sale_date'])
    for sale in sales:
        sale_time = vend.convert_date(sale['sale_date'])
        print(sale_time)
        sale_total += sale['total_price']
        if sale_time - last_sale_time > timedelta(minutes=30):
            tours.append({"sale_total":sale_total,"time":last_sale_time})
            last_sale_time = sale_time
            sale_total = 0
    #sheets.add_rows(LL_sheets_ID,sheet_ID,len(tours))
    split_sales = vend.split_sales(sales,[time(17,50,0)])
    for group in split_sales:
        print(sum([s['total_price'] for s in group]))
if __name__ == "__main__":
    main()
