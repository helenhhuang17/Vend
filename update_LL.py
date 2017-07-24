import update

LL_vend_ID = '1PHwnRbhq4F4Q4I1zYGWsUTMr-oHmKOnYczsdl7zjjyQ'
LL_sheets_ID = '1uIw28MRuF8pEukgpUrbXXyFLGkXc16PRar8aPt8xybg'

token = os.environ['token']
outlets = {'MTA':'01f9c6db-e35e-11e2-a415-bc764e10976c',
'GAR':'064dce89-c73d-11e5-ec2a-c92ca32c62a3',
'JFK':'605445f3-3846-11e2-b1f5-4040782fde00',
'BAS':'f92e438b-3db4-11e2-b1f5-4040782fde00'}

s = requests.Session()
s.headers.update({'User-Agent':'theharvardshop_LL',"Authorization":"Bearer %s" %token})

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
    r = update.get_sales(today,tomorrow,'MTA',LL_vend_ID)
    print(r)
    #for sale in r:
    #    if sale['']
    #row = today.day+2
    #range_name = "J{}:L{}".format(row,row)
    #sheets.update(trademarkSheetsId,range_name,[[jfk_total,mta_total,gar_total]])

if __name__ == "__main__":
    main()
