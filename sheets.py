from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage



# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Commission Updater'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def update(spreadsheetId,rangeName,values):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    value_range_body = {
        "range":rangeName,
        "values":values
    }
    result = service.spreadsheets().values().update(spreadsheetId=spreadsheetId,
    range=rangeName,valueInputOption='USER_ENTERED',body=value_range_body).execute()
    print(result)
def add_rows(spreadsheetId,sheetId,num):
    body = {
        "requests":[{
          "insertDimension": {
            "range": {
              "sheetId": sheetId,
              "dimension": "ROWS",
              "startIndex": 1,
              "endIndex": 1+num
            },
            "inheritFromBefore": False
          }
        }]
    }
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    result = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId,
        body=body).execute()
    print(result)

if __name__ == '__main__':
    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None
    trademarkSheetsId = '1uIw28MRuF8pEukgpUrbXXyFLGkXc16PRar8aPt8xybg'
    update(trademarkSheetsId,'K22',[[1]])
