from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Optional
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
import asyncio

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Instantiate FastAPI and templates
app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))
app.mount("/static", StaticFiles(directory="../app/static"), name="static")

# Setup Google Sheets credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(str(Path(BASE_DIR, 'credentials.json')), scope)
gc = gspread.authorize(credentials)

# Global cache
sheet_cache = []
cache_interval_seconds = 60

# Background task to refresh sheet cache
async def sheet_cache_refresher():
    global sheet_cache
    while True:
        try:
            logging.info("⏳ Refreshing Google Sheet cache...")
            sheet = gc.open_by_key(os.getenv('wksht_key')).worksheet(os.getenv('wksht_name'))
            expected_headers = sheet.row_values(1)
            sheet_cache = sheet.get_all_records(expected_headers=expected_headers)
            logging.info("✅ Sheet cache updated successfully.")
        except Exception as e:
            logging.error(f"❌ Error refreshing sheet cache: {e}")
        await asyncio.sleep(cache_interval_seconds)

# Start the background task on app startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(sheet_cache_refresher())

@app.get("/")
async def read_google_sheet(request: Request):
    return templates.TemplateResponse("readbyline.html", {"request": request, "result": None})

@app.post("/")
async def search_in_sheet(request: Request, search: Optional[str] = Form(None)):
    if not search:
        return templates.TemplateResponse("readbyline.html", {"request": request, "result": "Please enter an email address to search."})

    try:
        data = sheet_cache
        result = next((record for record in data if record['Email'] == search), None)
        if result is None:
            result = "User not found. Contact instructor"
        return templates.TemplateResponse("readbyline.html", {"request": request, "result": result})
    except Exception as e:
        logging.error(f"❌ An error occurred: {str(e)}")
        return templates.TemplateResponse("readbyline.html", {"request": request, "result": "An error occurred while searching. Please try again later."})
