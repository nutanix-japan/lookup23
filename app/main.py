from fastapi import FastAPI, Request, Form, WebSocket, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
import asyncio
from datetime import datetime
import time
import json
from collections import deque

# Load environment variables
load_dotenv()

# Setup custom log handler to capture logs
class MemoryLogHandler(logging.Handler):
    def __init__(self, max_entries=100):
        super().__init__()
        self.log_entries = deque(maxlen=max_entries)
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    def emit(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "message": self.formatter.format(record),
        }
        self.log_entries.append(log_entry)
    
    def get_logs(self):
        return list(self.log_entries)

# Setup logging
memory_handler = MemoryLogHandler(max_entries=100)
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), memory_handler]
)

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
cache_interval_seconds = 180
last_cache_refresh = None
cache_refresh_status = "idle"

# WebSocket connection for real-time logs
connected_clients = set()

# Broadcast new logs to all connected clients
async def broadcast_logs(new_log=None):
    if connected_clients:
        logs = memory_handler.get_logs()
        for client in connected_clients:
            try:
                await client.send_json({"type": "logs", "data": logs})
            except Exception:
                pass

# Override original logging handler to broadcast logs
original_emit = memory_handler.emit
def new_emit(record):
    original_emit(record)
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(broadcast_logs(), loop)
memory_handler.emit = new_emit

# Background task to refresh sheet cache
async def sheet_cache_refresher():
    global sheet_cache, last_cache_refresh, cache_refresh_status
    while True:
        try:
            logging.info("⏳ Refreshing Google Sheet cache...")
            cache_refresh_status = "refreshing"
            await broadcast_cache_status()
            
            sheet = gc.open_by_key(os.getenv('wksht_key')).worksheet(os.getenv('wksht_name'))
            expected_headers = sheet.row_values(1)
            sheet_cache = sheet.get_all_records(expected_headers=expected_headers)
            last_cache_refresh = datetime.now()
            cache_refresh_status = "idle"
            
            logging.info(f"✅ Sheet cache updated successfully. Cached {len(sheet_cache)} records.")
            await broadcast_cache_status()
        except Exception as e:
            cache_refresh_status = "error"
            logging.error(f"❌ Error refreshing sheet cache: {e}")
            await broadcast_cache_status()
        await asyncio.sleep(cache_interval_seconds)

# Function to broadcast cache status to connected clients
async def broadcast_cache_status():
    if connected_clients:
        cache_info = get_cache_info()
        for client in connected_clients:
            try:
                await client.send_json({"type": "cache_status", "data": cache_info})
            except Exception:
                pass

# Function to get current cache info
def get_cache_info():
    global last_cache_refresh, cache_refresh_status
    return {
        "records": len(sheet_cache),
        "last_refresh": last_cache_refresh.strftime("%Y-%m-%d %H:%M:%S") if last_cache_refresh else "Never",
        "next_refresh": (last_cache_refresh.timestamp() + cache_interval_seconds) if last_cache_refresh else None,
        "current_time": time.time(),
        "interval": cache_interval_seconds,
        "status": cache_refresh_status
    }

# Function to manually refresh cache
async def manual_refresh_cache():
    global sheet_cache, last_cache_refresh, cache_refresh_status
    try:
        logging.info("🔄 Manual cache refresh triggered...")
        cache_refresh_status = "refreshing"
        await broadcast_cache_status()
        
        sheet = gc.open_by_key(os.getenv('wksht_key')).worksheet(os.getenv('wksht_name'))
        expected_headers = sheet.row_values(1)
        sheet_cache = sheet.get_all_records(expected_headers=expected_headers)
        last_cache_refresh = datetime.now()
        cache_refresh_status = "idle"
        
        logging.info(f"✅ Sheet cache manually updated successfully. Cached {len(sheet_cache)} records.")
        await broadcast_cache_status()
        return {"status": "success", "message": "Cache refreshed successfully", "records": len(sheet_cache)}
    except Exception as e:
        cache_refresh_status = "error"
        error_msg = f"❌ Error refreshing sheet cache: {e}"
        logging.error(error_msg)
        await broadcast_cache_status()
        return {"status": "error", "message": error_msg}

# Start the background task on app startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(sheet_cache_refresher())

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        # Send initial logs and cache status
        await websocket.send_json({"type": "logs", "data": memory_handler.get_logs()})
        await websocket.send_json({"type": "cache_status", "data": get_cache_info()})
        
        # Keep connection alive and handle commands
        while True:
            data = await websocket.receive_text()
            if data == "refresh_cache":
                asyncio.create_task(manual_refresh_cache())
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        connected_clients.remove(websocket)

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

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "cache_info": get_cache_info(),
        "logs": memory_handler.get_logs()
    })

@app.post("/api/refresh-cache")
async def api_refresh_cache(background_tasks: BackgroundTasks):
    background_tasks.add_task(manual_refresh_cache)
    return JSONResponse({"status": "success", "message": "Cache refresh started"})

@app.get("/api/cache-status")
async def api_cache_status():
    return JSONResponse(get_cache_info())

@app.get("/api/logs")
async def api_logs():
    return JSONResponse({"logs": memory_handler.get_logs()})