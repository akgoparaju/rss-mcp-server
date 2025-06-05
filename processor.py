"""
RSS Processor - Fetches, parses, and filters RSS items
"""
import feedparser
import yaml
from datetime import datetime
from typing import List, Dict, Any
import hashlib
import os
import sys

class RSSProcessor:
    def __init__(self, config_file: str = "feeds.yaml"):
        # Use absolute path to ensure we can always write to the project directory
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.project_dir, config_file)
        self.feeds = []
        self.articles = []

    async def initialize(self):
        """Initialize the processor by loading feed configuration"""
        self.load_config()

    def load_config(self):
        """Load RSS feeds configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as file:
                config = yaml.safe_load(file)
                self.feeds = config if isinstance(config, list) else []
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found. Using default config.", file=sys.stderr)
            self.use_default_config()
        except Exception as e:
            print(f"Error loading config: {e}. Using default config.", file=sys.stderr)
            self.use_default_config()

    def use_default_config(self):
        """Use default configuration without creating a file"""
        self.feeds = [
            {
                "url": "https://insidegnss.com/feed/",
                "tags": ["C-band", "TrustPoint", "GPSIA", "PNT"]
            },
            {
                "url": "https://breakingdefense.com/feed/",
                "tags": ["LEO", "alt-PNT", "jamming", "military"]
            },
            {
                "url": "https://www.gpsworld.com/feed/",
                "tags": ["GPS", "GNSS", "navigation", "timing"]
            }
        ]

    def create_default_config(self):
        """Create a default feeds.yaml configuration"""
        default_feeds = [
            {
                "url": "https://insidegnss.com/feed/",
                "tags": ["C-band", "TrustPoint", "GPSIA", "PNT"]
            },
            {
                "url": "https://breakingdefense.com/feed/",
                "tags": ["LEO", "alt-PNT", "jamming", "military"]
            },
            {
                "url": "https://www.gpsworld.com/feed/",
                "tags": ["GPS", "GNSS", "navigation", "timing"]
            }
        ]

        try:
            with open(self.config_file, 'w') as file:
                yaml.dump(default_feeds, file, default_flow_style=False)
            print(f"Created default config at {self.config_file}", file=sys.stderr)
        except Exception as e:
            print(f"Could not create config file: {e}. Using in-memory config.", file=sys.stderr)

        self.feeds = default_feeds

    async def update_feeds(self):
        """Fetch and parse all configured RSS feeds"""
        self.articles = []

        for feed_config in self.feeds:
            url = feed_config.get('url')
            tags = feed_config.get('tags', [])

            if not url:
                continue

            try:
                print(f"Fetching feed: {url}")
                feed = feedparser.parse(url)

                for entry in feed.entries:
                    article = self.process_entry(entry, tags)
                    if article and self.should_include_article(article, tags):
                        self.articles.append(article)

            except Exception as e:
                print(f"Error processing feed {url}: {e}")

    def process_entry(self, entry, feed_tags: List[str]) -> Dict[str, Any]:
        """Process a single RSS entry into a standardized article format"""
        try:
            # Generate unique ID for the article
            article_id = hashlib.md5(
                f"{entry.get('link', '')}{entry.get('title', '')}".encode()
            ).hexdigest()

            # Parse publication date
            pub_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                pub_date = datetime(*entry.updated_parsed[:6]).isoformat()

            article = {
                "id": article_id,
                "title": entry.get('title', ''),
                "link": entry.get('link', ''),
                "description": entry.get('description', ''),
                "summary": entry.get('summary', ''),
                "published": pub_date,
                "author": entry.get('author', ''),
                "feed_tags": feed_tags,
                "content": self.extract_content(entry)
            }

            return article

        except Exception as e:
            print(f"Error processing entry: {e}")
            return None

    def extract_content(self, entry) -> str:
        """Extract content from RSS entry"""
        content = ""

        # Try different content fields
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if isinstance(entry.content, list) else str(entry.content)
        elif hasattr(entry, 'summary') and entry.summary:
            content = entry.summary
        elif hasattr(entry, 'description') and entry.description:
            content = entry.description

        return content

    def should_include_article(self, article: Dict[str, Any], feed_tags: List[str]) -> bool:
        """Determine if article should be included based on tags"""
        if not feed_tags:
            return True

        # Check if any feed tags appear in title or content
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        description = article.get('description', '').lower()

        text_to_search = f"{title} {content} {description}"

        for tag in feed_tags:
            if tag.lower() in text_to_search:
                return True

        return False

    async def get_all_articles(self) -> List[Dict[str, Any]]:
        """Get all articles from the last fetch"""
        return self.articles

    async def search_articles(self, query: str, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Search articles by query and optionally filter by tags"""
        if not query and not tags:
            return self.articles

        results = []
        query_lower = query.lower() if query else ""
        tags_lower = [tag.lower() for tag in tags] if tags else []

        for article in self.articles:
            # Search in title, content, and description
            searchable_text = f"{article.get('title', '')} {article.get('content', '')} {article.get('description', '')}".lower()

            # Check query match
            query_match = not query or query_lower in searchable_text

            # Check tags match
            tags_match = True
            if tags_lower:
                feed_tags_lower = [tag.lower() for tag in article.get('feed_tags', [])]
                tags_match = any(tag in feed_tags_lower for tag in tags_lower)

            if query_match and tags_match:
                results.append(article)

        return results
