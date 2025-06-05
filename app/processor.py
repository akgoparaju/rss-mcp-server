import feedparser
import yaml
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from state import save_entry_if_unseen

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load feed configuration
with open("feeds.yaml") as f:
    CONFIG = yaml.safe_load(f)

def fetch_and_filter():
    logger.info("Fetching and filtering RSS feeds...")
    for feed in CONFIG["feeds"]:
        url, tags = feed["url"], feed["tags"]
        parsed = feedparser.parse(url)
        matched = 0
        for entry in parsed.entries:
            content = f"{entry.title}\n{entry.get('summary', '')}"
            content_lower = content.lower()
            if any(tag.lower() in content_lower for tag in tags):
                id_ = hashlib.md5(entry.link.encode()).hexdigest()
                obj = {
                    "id": id_,
                    "title": entry.title,
                    "summary": entry.get("summary", ""),
                    "link": entry.link,
                    "published": entry.get("published", str(datetime.utcnow())),
                    "matched_tags": tags,
                    "llm_text": content,
                }
                save_entry_if_unseen(obj)
                logger.info(f"[MATCH] Saved: {entry.title} | ID: {id_}")
                matched += 1
        logger.info(f"Feed '{url}' → {matched} matches")
