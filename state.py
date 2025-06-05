"""
State Manager - Tracks read/unread state of RSS articles
"""
import json
import os
from typing import Set, List, Dict, Any
from datetime import datetime
import sys

class StateManager:
    def __init__(self, state_file: str = "state.json"):
        # Use absolute path to ensure we can always write to the project directory
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.state_file = os.path.join(self.project_dir, state_file)
        self.read_articles: Set[str] = set()
        self.load_state()

    def load_state(self):
        """Load read articles state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as file:
                    data = json.load(file)
                    self.read_articles = set(data.get('read_articles', []))
        except Exception as e:
            print(f"Error loading state: {e}. Starting with empty state.", file=sys.stderr)
            self.read_articles = set()

    def save_state(self):
        """Save read articles state to file"""
        try:
            data = {
                'read_articles': list(self.read_articles),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.state_file, 'w') as file:
                json.dump(data, file, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}. State will not persist.", file=sys.stderr)

    def mark_read(self, article_id: str):
        """Mark a single article as read"""
        self.read_articles.add(article_id)
        self.save_state()

    def mark_all_read(self, articles: List[Dict[str, Any]] = None):
        """Mark all articles as read"""
        if articles:
            for article in articles:
                self.read_articles.add(article.get('id'))
        self.save_state()

    def is_read(self, article_id: str) -> bool:
        """Check if an article has been read"""
        return article_id in self.read_articles

    def get_unread_items(self, articles: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all unread articles from the provided list"""
        if not articles:
            return []

        unread = []
        for article in articles:
            article_id = article.get('id')
            if article_id and not self.is_read(article_id):
                unread.append(article)

        return unread

    def get_read_count(self) -> int:
        """Get total number of read articles"""
        return len(self.read_articles)

    def clear_read_state(self):
        """Clear all read state (mark all as unread)"""
        self.read_articles.clear()
        self.save_state()
