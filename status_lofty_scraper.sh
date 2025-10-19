#!/bin/bash


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/lofty_scraper.pid"
LOG_FILE="$SCRIPT_DIR/logs/lofty_scraper.log"
DATA_DIR="$SCRIPT_DIR/data/lofty"

echo "="*80
echo "📊 LOFTY.AI SCRAPER STATUS"
echo "="*80
echo ""

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ Status: RUNNING"
        echo "   PID: $PID"
        
        START_TIME=$(ps -p $PID -o lstart=)
        echo "   Started: $START_TIME"
    else
        echo "❌ Status: NOT RUNNING (stale PID file)"
    fi
else
    echo "❌ Status: NOT RUNNING"
fi

echo ""

if [ -d "$DATA_DIR" ]; then
    PROPERTY_FILES=$(ls -1 "$DATA_DIR"/properties_*.json 2>/dev/null | wc -l)
    echo "📁 Data Directory: $DATA_DIR"
    echo "   Property files: $PROPERTY_FILES"
    
    if [ $PROPERTY_FILES -gt 0 ]; then
        LATEST_FILE=$(ls -t "$DATA_DIR"/properties_*.json 2>/dev/null | head -1)
        LAST_SCRAPE=$(stat -c %y "$LATEST_FILE" 2>/dev/null | cut -d'.' -f1)
        PROPERTY_COUNT=$(python3 -c "import json; print(len(json.load(open('$LATEST_FILE'))))" 2>/dev/null || echo "N/A")
        
        echo "   Last scrape: $LAST_SCRAPE"
        echo "   Properties scraped: $PROPERTY_COUNT"
    fi
else
    echo "📁 Data Directory: Not created yet"
fi

echo ""

if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
    echo "📝 Log File: $LOG_FILE"
    echo "   Size: $LOG_SIZE"
    echo ""
    echo "   Last 10 lines:"
    echo "   " + "-"*76
    tail -10 "$LOG_FILE" | sed 's/^/   /'
else
    echo "📝 Log File: Not created yet"
fi

echo ""
echo "="*80
