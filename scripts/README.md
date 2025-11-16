# AccuDoc Scripts

Standalone scripts and utilities for AccuDoc.

## Files

### `collaboration_server.py`
WebSocket server for real-time collaboration features.

**Usage:**
```bash
python scripts/collaboration_server.py --port 8765 --db collaboration.db
```

**Options:**
- `--port`: WebSocket server port (default: 8765)
- `--db`: Database file path (default: collaboration.db)
- `--slack-webhook`: Slack webhook URL for notifications
- `--teams-webhook`: Microsoft Teams webhook URL for notifications

**Features:**
- Real-time document editing synchronization
- User presence tracking
- Comment and review notifications
- WebSocket-based communication

**Started by CLI:**
```bash
python accudoc_cli.py start-collab-server --port 8765
```

The server runs as a background process and can be stopped with:
```bash
python accudoc_cli.py stop-collab-server
```
