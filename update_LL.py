import update
import os
import requests
import sys
from datetime import date, datetime, timedelta, time
import sheets
import vend

id_dict = {
    "HIC":"e52b2846-e93d-11e5-f98b-49ebcf6844db",
    "LL":"e52b2846-e93d-11e5-f98b-4867acedc6be",
    "Charles":"06e08a30-ee3d-11e7-ec24-69d6803d9061",
    "Trademark":"e52b2846-e93d-11e5-f98b-4867baceded1"
}
LL_vend_ID = 'e52b2846-e93d-11e5-f98b-4867acedc6be'
LL_sheets_ID = '1PHwnRbhq4F4Q4I1zYGWsUTMr-oHmKOnYczsdl7zjjyQ'
sheet_ID = 1964826995
split = [time(12,0,0)]
split = split[::-1]

# TOKEN = os.environ['token']
TOKEN = '2tQzNrcZpJ7vDDXgznMJzk_IeA7KG9IHxhifABBz'
outlets = {'MTA':'01f9c6db-e35e-11e2-a415-bc764e10976c',
'GAR':'064dce89-c73d-11e5-ec2a-c92ca32c62a3',
'JFK':'605445f3-3846-11e2-b1f5-4040782fde00',
'BAS':'f92e438b-3db4-11e2-b1f5-4040782fde00'}

s = requests.Session()
s.headers.update({'User-Agent':'theharvardshop commission',"Authorization":"Bearer {}".format(TOKEN)})


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
    split_sales = vend.split_sales(sales,split)

    sheets_payload = []
    groups = len(split_sales)
    print("{} groups of sales".format(groups))
    for group in split_sales:
        group_date = vend.convert_date(group[0]['sale_date']).date()
        group_time = vend.convert_date(group[0]['sale_date']).time()
        group_total = sum([s['total_price'] for s in group])
        triple = [group_date,group_time,group_total]
        sheets_payload.append([str(e) for e in triple])
        print(triple)
    sheets.add_rows(LL_sheets_ID,sheet_ID,len(split)+1)
    sheets.update(LL_sheets_ID,"B2:D{}".format(2+len(split_sales)),sheets_payload)
if __name__ == "__main__":
    main()
