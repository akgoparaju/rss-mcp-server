import feedparser, yaml, hashlib, json
from datetime import datetime
from pathlib import Path
from .state import save_entry_if_unseen

with open("app/feeds.yaml") as f:
    CONFIG = yaml.safe_load(f)

def fetch_and_filter():
    for feed in CONFIG["feeds"]:
        url, tags = feed["url"], feed["tags"]
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            content = f"{entry.title}\n{entry.get('summary', '')}"
            if any(tag.lower() in content.lower() for tag in tags):
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
