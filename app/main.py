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
from os import path
import logging
from pathlib import Path

# Load pydantic data validation for GET/POST parameters

class search(BaseModel):
    search: Optional[str] = None

# Load get env variables from the .env file
load_dotenv()

#Instantiate FastAPI object and jinja templates
app = FastAPI()

#Templates mount
#Modified for container runtime
BASE_DIR = Path(__file__).resolve().parent  
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))


# FastAPI mount for static directory for css reference
# Modified for container runtime and path
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# Load Google Sheets credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '/app/credentials.json', scope)

gc = gspread.authorize(credentials)

@app.get("/")
async def read_google_sheet(request: Request):
    return templates.TemplateResponse("readbyline.html", {"request": request, "result": None})

@app.post("/")
async def search_in_sheet(request: Request, search: str = Form(...)):
    sheet = gc.open_by_key(os.getenv('wksht_key')).worksheet(os.getenv('wksht_name'))
    expected_headers = sheet.row_values(1)
    data = sheet.get_all_records(expected_headers=expected_headers)

    result = None
    for record in data:
        if record['Email'] == search:
            result = record
            break
        
    if result is None:
        result = "User not found. Contact instructor"

    return templates.TemplateResponse("readbyline.html", {"request": request, "result": result})
