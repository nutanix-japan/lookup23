from fastapi import FastAPI, Request, Form, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.datastructures import URL
from google.oauth2 import service_account

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Set up credentials for Google Sheets API
creds = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

# Mount the static files directory to the /static path
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define function to search for rows in the sheet
def search_sheet(spreadsheet_id, sheet_name, search_col, search_term):
    service = build('sheets', 'v4', credentials=creds)
    sheet_range = f'{sheet_name}!A:ZZ'  # adjust the range as per your sheet data
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=sheet_range).execute()
    rows = result.get('values', [])

    if not rows:
        return []

    # Find the column index to search in
    headers = rows[0]
    search_col_index = headers.index(search_col)

    # Filter the rows based on search term
    filtered_rows = [headers]
    for row in rows[1:]:
        if row[search_col_index] == search_term:
            filtered_rows.append(row)
    print(rows[0])
    print(rows[1])
    print(len(rows[0]))
    return filtered_rows

r1_r2_map = {
    "Consultant Information": [0,1],
    "Nutanix Cluster Information": [2,3,4,5,6],
    "Lab - Consolidated Storage": [7,8,9,10,11,12,13,14],
    "Calm Iaas":[15,16,17],
    "Disaster recovery":[18,19,20,21,22,23],
    "NDB":[24,25,26],
    "Lab - OCP (Openshift, Objects, Files)":[27,28,29,30,31,32,33,34],
    "Lab GTS23 - Migrate":[35,36,37,38,39,40],
    "Lab GTS23 - Secure":[41,42,43]
}


@app.get("/")
async def search(request: Request, search_term: str = Form(None)):
    if search_term is not None:
        # Search the sheet for matching rows
        spreadsheet_id = "1meMee6yCvtplZCkljknSYtdFECBEPauw8kn-1YB5x7A"
        sheet_name = "Sheet1"
        search_col = "Email"
        rows = search_sheet(spreadsheet_id, sheet_name, search_col, search_term)
        return templates.TemplateResponse("search.html", {"request": request, "rows": rows, "map": r1_r2_map})
    else:
        return templates.TemplateResponse("search.html", {"request": request, "rows": None})

