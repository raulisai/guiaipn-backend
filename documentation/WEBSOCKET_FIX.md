# WebSocket WSGI Protocol Error - Fix

## Problem
```
AssertionError: write() before start_response
```

This error occurred during WebSocket handshake because Werkzeug's development server has compatibility issues with WebSocket upgrades in Flask-SocketIO.

## Root Cause
- Flask-SocketIO with `async_mode="threading"` uses Werkzeug's development server
- Werkzeug's WSGI implementation has known issues with WebSocket protocol upgrades
- When rejecting connections or handling errors during handshake, WSGI response status wasn't being set properly

## Solution
Switched to **gevent** as the async mode, which provides:
- Proper WebSocket protocol handling
- Green threads (greenlets) for concurrent connections
- Production-ready WSGI server
- No WSGI protocol violations
- Python 3.12+ compatibility (eventlet is incompatible due to missing distutils)

## Changes Made

### 1. Added gevent dependencies
**File:** `requirements.txt`
```python
gevent==24.2.1
gevent-websocket==0.10.1
numpy>=2.3.0  # Required for OpenAI with gevent monkey patching
pandas>=2.3.0  # Required for OpenAI with gevent monkey patching
```

### 2. Updated SocketIO async mode
**File:** `app/extensions.py`
```python
socketio.init_app(
    app,
    cors_allowed_origins=Config.CORS_ORIGINS,
    async_mode="gevent",  # Changed from "threading"
    # ... other settings
)
```

### 3. Automatic gevent monkey patching
**File:** `run.py`
```python
# Flask-SocketIO handles monkey patching automatically
# when async_mode="gevent" is set
# No manual monkey.patch_all() needed!
```

Flask-SocketIO automatically applies gevent monkey patching when it detects `async_mode="gevent"`, avoiding import-time conflicts with libraries like OpenAI that have lazy imports.

### 4. Enhanced connection error handling
**File:** `app/socket_events/connection.py`
- Return `False` to reject connections cleanly
- Added traceback logging for debugging
- No emit() calls during handshake failures

## Installation
```bash
pip install gevent==24.2.1 gevent-websocket==0.10.1
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

## Testing
1. Start the server: `python run.py`
2. Connect via WebSocket from frontend
3. Verify no WSGI errors in console
4. Check that connections are properly established/rejected

## Benefits
- ✅ No more WSGI protocol errors
- ✅ Better WebSocket performance
- ✅ Production-ready async handling
- ✅ Proper connection rejection
- ✅ Clean error logging

## Notes
- **Gevent** uses greenlets (green threads with cooperative multitasking)
- All blocking I/O is automatically patched via Flask-SocketIO's automatic monkey patching
- Compatible with Redis, Supabase, and OpenAI clients
- Python 3.12+ compatible (unlike eventlet which requires distutils)
- No code changes needed in socket event handlers
- More actively maintained than eventlet
- **Important:** numpy and pandas are required because gevent's monkey patching triggers OpenAI's lazy imports. Without these packages, you'll get `MissingDependencyError` during startup.
