#!/bin/bash


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/lofty_scraper.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "❌ Lofty scraper is not running (no PID file found)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
    echo "🛑 Stopping Lofty scraper (PID: $PID)..."
    kill $PID
    
    sleep 2
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Process still running, forcing stop..."
        kill -9 $PID
    fi
    
    rm "$PID_FILE"
    echo "✅ Lofty scraper stopped successfully!"
else
    echo "⚠️  Process not found (PID: $PID)"
    echo "   Removing stale PID file..."
    rm "$PID_FILE"
fi
