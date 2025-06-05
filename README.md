# 📡 RSS MCP Server

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com/your-repo/rss-mcp-server)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple)](https://modelcontextprotocol.io)

A modular Model Context Protocol (MCP) server for tracking, filtering, and surfacing PNT/GNSS news from custom RSS feeds with natural language interface via Claude Desktop.

## ✨ Features

- 🔗 **Native MCP Integration** - Direct integration with Claude Desktop
- 📰 **RSS Feed Processing** - Fetches and parses multiple RSS feeds
- 🏷️ **Tag-based Filtering** - Content filtering using configurable tags
- 💬 **Natural Language Interface** - AI-powered RSS management
- 📊 **State Management** - Persistent read/unread article tracking
- 🔍 **Search Capabilities** - Keyword and tag-based article search
- 🛡️ **Error Handling** - Graceful fallbacks and error recovery

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Claude Desktop
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
cd rss-mcp-server

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install mcp feedparser pyyaml httpx
```

### Configuration

1. **Create feeds.yaml** (if not exists):
```yaml
- url: https://insidegnss.com/feed/
  tags: [C-band, TrustPoint, GPSIA, LEO, PNT]
- url: https://spacenews.com/feed/
  tags: [LEO, spoofing, spectrum]
- url: https://www.gpsworld.com/feed/
  tags: [GNSS, spoof, jamming, M-code]
```

2. **Configure Claude Desktop**:

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "rss-mcp-server": {
      "command": "/path/to/your/project/.venv/bin/python",
      "args": ["/path/to/your/project/main.py"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

**⚠️ Replace paths with your actual project location**

3. **Restart Claude Desktop** completely (quit and reopen)

### Testing

```bash
# Test server locally
python main.py
# Should output: "RSS MCP Server initialized successfully"
```

## 🤖 Usage

Once integrated with Claude Desktop, use natural language commands:

```
"Update my RSS feeds"
"Show me articles about GPS jamming"
"Search for LEO satellite articles"
"Mark the first 5 articles as read"
"Find articles about spoofing"
"Show me 10 recent unread articles"
```

## 📡 MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `update_rss_feeds` | Fetch latest articles from all feeds | None |
| `get_unread_articles` | Get unread articles | `limit` (optional) |
| `mark_articles_read` | Mark articles as read | `article_ids` (optional) |
| `search_articles` | Search articles by keywords | `query`, `tags` (optional) |

## 📊 MCP Resources

| Resource URI | Description |
|--------------|-------------|
| `rss://feeds/unread` | All unread articles (JSON) |
| `rss://feeds/all` | All articles (JSON) |

## 📁 Project Structure

```
rss-mcp-server/
├── main.py              # MCP server implementation
├── processor.py         # RSS feed processing logic
├── state.py            # State management for read/unread tracking
├── feeds.yaml          # Feed configuration (direct list format)
├── state.json          # Runtime state (auto-created)
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .venv/             # Virtual environment
```

## ⚙️ Configuration Details

### feeds.yaml Format

**✅ Correct format (direct list):**
```yaml
- url: https://example.com/feed/
  tags: [tag1, tag2, tag3]
- url: https://another.com/rss/
  tags: [tag4, tag5]
```

**❌ Incorrect format (with wrapper):**
```yaml
feeds:  # Don't use this wrapper
  - url: https://example.com/feed/
```

### Tags

Tags are used for:
- Content filtering during search
- Categorizing articles by topic
- Enhancing search relevance

Example tags for PNT/GNSS content:
- `GPS`, `GNSS`, `PNT`
- `jamming`, `spoofing`, `interference`
- `LEO`, `MEO`, `satellites`
- `military`, `defense`, `civilian`
- `M-code`, `anti-jam`, `resilient`

## 🔧 Troubleshooting

### Common Issues

**Server not appearing in Claude Desktop:**
- Verify `claude_desktop_config.json` syntax and paths
- Ensure all paths are absolute
- Restart Claude Desktop completely

**Import errors:**
```bash
pip install mcp feedparser pyyaml httpx
```

**feeds.yaml format errors:**
- Use direct list format (start with `-`)
- No `feeds:` wrapper needed
- Ensure proper YAML syntax

**File permission errors:**
- Ensure write permissions for `state.json`
- Check directory permissions

### Debug Steps

1. **Test locally:** `python main.py`
2. **Check dependencies:** `pip list | grep -E "(mcp|feedparser|pyyaml|httpx)"`
3. **Validate config:** Check Claude Desktop logs
4. **Verify feeds:** Test feed URLs in browser

## 🧪 Development

### Running Tests

```bash
# Test RSS feed processing
python -c "from processor import RSSProcessor; import asyncio; asyncio.run(RSSProcessor().initialize())"

# Test state management
python -c "from state import StateManager; sm = StateManager(); print('State manager working')"
```

### Adding New Feeds

1. Add feed URL to `feeds.yaml`
2. Configure appropriate tags
3. Restart the MCP server
4. Update feeds: "Update my RSS feeds"

### Debugging

Enable debug output by modifying `main.py`:
```python
import sys
print("Debug info", file=sys.stderr)
```

## 📈 Performance

- **Feed Updates**: ~2-5 seconds for 3-5 feeds
- **Article Search**: <1 second for typical queries
- **State Persistence**: Automatic on read/unread changes
- **Memory Usage**: ~10-20MB typical operation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: Create GitHub issue with logs
- **Questions**: Tag @anil.goparaju
- **Documentation**: See Google Drive docs

## 🎯 Use Cases

**Daily News Briefing:**
```
"Update feeds and show me unread articles about GPS jamming and spoofing"
```

**Research Assistance:**
```
"Search for articles about LEO PNT systems published this week"
```

**Competitive Intelligence:**
```
"Find articles mentioning TrustPoint or military navigation systems"
```

**Content Curation:**
```
"Show me all unread articles, then mark the first 10 as read"
```

## 📊 Sample Output

When you search for "GPS jamming", you get structured results:

```json
{
  "count": 3,
  "articles": [
    {
      "id": "251bc714...",
      "title": "U.S. Army Taking a Layered Approach to PNT",
      "link": "https://insidegnss.com/...",
      "published": "2025-06-03T16:58:20",
      "author": "Renee Knight",
      "feed_tags": ["C-band", "TrustPoint", "GPSIA", "LEO", "PNT"],
      "content": "...anti-jamming capabilities..."
    }
  ]
}
```

---

**Last Updated:** June 5, 2025  
**Status:** ✅ Production Ready
