import csv
import requests

token = '2tQzNrcZpJ7vDDXgznMJzk_0iRjJapAUutvwrrqu'
MTA = '01f9c6db-e35e-11e2-a415-bc764e10976c'
GAR = '064dce89-c73d-11e5-ec2a-c92ca32c62a3'

def get_id(sku):
    payload = {"sku":sku}
    r = requests.get("https://harvardshop.vendhq.com/api/products",params=payload,headers={"Authorization":"Bearer %s" %token})
    try:
        return r.json()['products'][0]['id']
    except KeyError:
        "invalid key (get_id)"

with open('stock_count.csv',newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) != 2:
            break
        row = [int(e) for e in row]
        sku, count = row
        payload = {"id":get_id(sku),"inventory":[{"outlet_id":GAR,"count":count}]}
        print(get_id(sku))
        print(payload)
        r = requests.post("https://harvardshop.vendhq.com/api/products",data=payload,headers={"Authorization":"Bearer %s" %token})
        print(r.text)
