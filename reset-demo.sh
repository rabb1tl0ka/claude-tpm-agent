#!/bin/bash
# reset-demo.sh - Reset vault to demo-ready state

set -e  # Exit on error

echo "🔄 Resetting vault to demo-ready state..."

# Reset vault files to last committed state (git)
git checkout HEAD -- vaults/peaklogistics/

# Clean agent artifacts (logs, memory, inboxes, outboxes)
echo "🧹 Cleaning agent artifacts..."

# Remove role logs
find vaults/peaklogistics/agent/logs -type f -name "*.md" -delete 2>/dev/null || true

# Remove role memory files
find vaults/peaklogistics/agent/memory -type f -name "*.md" -delete 2>/dev/null || true

# Clean inboxes (keep .gitkeep)
find vaults/peaklogistics/agent/inbox -type f ! -name '.gitkeep' -delete 2>/dev/null || true

# Clean outboxes (keep .gitkeep)
find vaults/peaklogistics/agent/outbox -type f ! -name '.gitkeep' -delete 2>/dev/null || true

# Reset sessions
if [ -f "sessions/sessions.json" ]; then
    echo "🗑️  Removing sessions.json..."
    rm -f sessions/sessions.json
fi

echo ""
echo "✅ Demo reset complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Verify: python3 runner.py --dry-run"
echo "   2. Start demo: See DEMO-SCRIPT.md"
echo ""
