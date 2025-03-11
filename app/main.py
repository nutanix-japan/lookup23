from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Optional
import os
from dotenv import load_dotenv
from pathlib import Path
import logging

# Load environment variables from the .env file
load_dotenv()

# Instantiate FastAPI object and jinja templates
app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

# FastAPI mount for static directory for css reference
app.mount("/static", StaticFiles(directory="../app/static"), name="static")

# Load Google Sheets credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('../credentials.json', scope)

gc = gspread.authorize(credentials)

@app.get("/")
async def read_google_sheet(request: Request):
    return templates.TemplateResponse("readbyline.html", {"request": request, "result": None})

@app.post("/")
async def search_in_sheet(request: Request, search: Optional[str] = Form(None)):
    if not search:
        return templates.TemplateResponse("readbyline.html", {"request": request, "result": "Please enter an email address to search."})

    try:
        sheet = gc.open_by_key(os.getenv('wksht_key')).worksheet(os.getenv('wksht_name'))
        expected_headers = sheet.row_values(1)
        data = sheet.get_all_records(expected_headers=expected_headers)

        result = next((record for record in data if record['Email'] == search), None)
        
        if result is None:
            result = "User not found. Contact instructor"

        return templates.TemplateResponse("readbyline.html", {"request": request, "result": result})
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return templates.TemplateResponse("readbyline.html", {"request": request, "result": "An error occurred while searching. Please try again later."})