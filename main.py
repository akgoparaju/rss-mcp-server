from fastapi import FastAPI
from app.processor import fetch_and_filter
from app.state import get_unread, mark_all_read

app = FastAPI()

@app.get("/rss/unread")
def get_unread_entries():
    return get_unread()

@app.post("/rss/update")
def update_feed():
    fetch_and_filter()
    return {"status": "updated"}

@app.post("/rss/mark-read")
def mark_as_read():
    mark_all_read()
    return {"status": "marked read"}
