from fastapi import FastAPI
import logging
from app.processor import fetch_and_filter
from app.state import get_unread, mark_all_read

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/rss/unread")
def get_unread_entries():
    logger.info("GET /rss/unread called")
    return get_unread()

@app.get("/status")
def status():
    return {"status": "OK"}

@app.post("/rss/update")
def update_feed():
    logger.info("POST /rss/update called")
    fetch_and_filter()
    return {"status": "updated"}

@app.post("/rss/mark-read")
def mark_as_read():
    logger.info("POST /rss/mark-read called")
    mark_all_read()
    return {"status": "marked read"}
