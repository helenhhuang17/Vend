import requests
import os
import json

token = os.environ['token']
s = requests.Session()
s.headers.update({'User-Agent':'theharvardshop_stocktools_JS',"Authorization":"Bearer %s" %token})

url = 'https://harvardshop.vendhq.com/reporting/api/1/report'
params = {"outlet":"01f9c6db-e35e-11e2-a415-bc764e10976c",
    "dimensions":"",
    "direction":"descending"
    }
r = s.get(url,data=params)
print(r.json())
