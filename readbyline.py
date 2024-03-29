from fastapi import FastAPI, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from fastapi.templating import Jinja2Templates
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydantic import BaseModel
from typing import Optional, Annotated
import os
from dotenv import load_dotenv

# Load pydantic data validation for GET/POST parameters

class search(BaseModel):
    search: Optional[str] = None

# Load get env variables from the .env file
load_dotenv()

#Instantiate FastAPI object and jinja templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# FastAPI mount for static directory for css reference 
app.mount("/static", StaticFiles(directory="static", html = True), name="site")


# Load Google Sheets credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials.json', scope)
print(credentials)
gc = gspread.authorize(credentials)

@app.get("/")
async def read_google_sheet(request: Request):
    return templates.TemplateResponse("readbyline.html", {"request": request, "result": None})

@app.post("/")
async def search_in_sheet(request: Request, search: str = Form(...)):
    #sheet = gc.open_by_key(os.getenv('wksht_key')).get_worksheet_by_id(int(os.getenv('wksht_id')))
    sheet = gc.open_by_key(os.getenv('wksht_key')).worksheet(os.getenv('wksht_name'))
    expected_headers = sheet.row_values(1)
    # print(f"Expected Headers: {expected_headers}")
    data = sheet.get_all_records(expected_headers=expected_headers)

    result = None
    for record in data:
        if record['Email'] == search:
            result = record
            break
        
    if result is None:
        result = "User not found. Contact instructor"

    return templates.TemplateResponse("readbyline.html", {"request": request, "result": result})
