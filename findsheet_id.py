import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build

spreadsheetId = "1meMee6yCvtplZCkljknSYtdFECBEPauw8kn-1YB5x7A"  # Please set the Spreadsheet Id.


# Set up credentials for Google Sheets API
creds = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

client = gspread.authorize(creds)
sh = client.open_by_key(spreadsheetId)
worksheet_list = sh.worksheets()
for sheet in worksheet_list:
    print('sheetName: {}, sheetId(GID): {}'.format(sheet.title, sheet.id))