#!/bin/bash


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/lofty_scraper.log"
PID_FILE="$SCRIPT_DIR/lofty_scraper.pid"

mkdir -p "$LOG_DIR"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ Lofty scraper is already running (PID: $PID)"
        echo "   To stop it, run: ./stop_lofty_scraper.sh"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

echo "🚀 Starting Lofty.ai automated scraper..."
echo "📁 Working directory: $SCRIPT_DIR"
echo "📝 Log file: $LOG_FILE"
echo ""

export SCRAPER_INTERVAL_HOURS=${SCRAPER_INTERVAL_HOURS:-3}

cd "$SCRIPT_DIR"
nohup python3 run_lofty_scheduler.py >> "$LOG_FILE" 2>&1 &
SCRAPER_PID=$!

echo $SCRAPER_PID > "$PID_FILE"

echo "✅ Lofty scraper started successfully!"
echo "   PID: $SCRAPER_PID"
echo "   Interval: Every $SCRAPER_INTERVAL_HOURS hours"
echo ""
echo "📊 To view logs:"
echo "   tail -f $LOG_FILE"
echo ""
echo "🛑 To stop the scraper:"
echo "   ./stop_lofty_scraper.sh"
echo ""
