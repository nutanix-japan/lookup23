from fastapi import FastAPI, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from fastapi.templating import Jinja2Templates
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydantic import BaseModel
from typing import Optional, Annotated

class search(BaseModel):
    search: Optional[str] = None

#Enter sheet values here
wksht_key="1meMee6yCvtplZCkljknSYtdFECBEPauw8kn-1YB5x7A"
wksht_id=547612463

#Instantiate FastAPI object and jinja templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# FastAPI mount for static directory for css reference 
app.mount("/static", StaticFiles(directory="static", html = True), name="site")


# Load Google Sheets credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials.json', scope)
gc = gspread.authorize(credentials)

@app.get("/")
async def read_google_sheet(request: Request):
    return templates.TemplateResponse("readbyline.html", {"request": request, "result": None})

@app.post("/")
async def search_in_sheet(request: Request, search: str = Form(...)):
    sheet = gc.open_by_key(wksht_key).get_worksheet_by_id(wksht_id)
    expected_headers = sheet.row_values(1)
    # print(f"Expected Headers: {expected_headers}")
    data = sheet.get_all_records(expected_headers=expected_headers)

    result = None
    for record in data:
        if record['Email'] == search:
            result = record
            break

    return templates.TemplateResponse("readbyline.html", {"request": request, "result": result})
