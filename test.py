from shift_planning import ShiftPlanning
import requests
import json
key = "2e7289b19cb16e522db15754f1f156279621d519"
url = 'https://www.humanity.com/api/'
#sp = ShiftPlanning(key,'john.shen@mail.hsa.net','Thspass00')
headers = {'Content-type': 'application/x-www-form-urlencoded'}

data = {
  "key": key,
  "request": {
    "module": "staff.login",
    "method": "GET",
    "username": "john.shen@mail.hsa.net",
    "password": "Thspass00"
  }
}

response = requests.post(url,data=json.dumps(data))

try:
    print(response.json())
except:
    print(response)
