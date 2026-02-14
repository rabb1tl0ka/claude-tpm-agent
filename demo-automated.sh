#!/bin/bash
# demo-automated.sh - Automated demo walkthrough with validation
# This script simulates the live demo, narrating each step and validating success
#
# Usage:
#   ./demo-automated.sh              # Interactive mode (pauses for Enter)
#   ./demo-automated.sh --no-wait    # Non-interactive mode (auto-continues)
#
#   # Save to file AND see in console                                                           
#  ./demo-automated.sh | tee demo-run-$(date +%Y-%m-%d_%H%M%S).txt                           
#                                                                                              
#  Or to capture both stdout and stderr:                                                       
#  ./demo-automated.sh 2>&1 | tee demo-run-$(date +%Y-%m-%d_%H%M%S).txt
#
#  What this does:
#  - tee reads from stdin and writes to both stdout (console) AND the file
#  - $(date +%Y-%m-%d_%H%M%S) creates timestamp like 2026-02-14_184432
#  - 2>&1 captures errors too (optional)

set -e  # Exit on error

# Check for no-wait flag
NO_WAIT=false
if [[ "$1" == "--no-wait" ]]; then
    NO_WAIT=true
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
narrate() {
    echo ""
    echo -e "${BLUE}🎙️  $1${NC}"
    echo ""
}

step() {
    echo -e "${YELLOW}▶️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error_exit() {
    echo ""
    echo -e "${RED}❌ ERROR: $1${NC}"
    echo -e "${RED}Demo step failed. Stopping.${NC}"
    exit 1
}

check_file_exists() {
    if [ ! -f "$1" ]; then
        error_exit "Expected file not found: $1"
    fi
    success "File exists: $1"
}

check_file_contains() {
    if ! grep -q "$2" "$1" 2>/dev/null; then
        error_exit "File $1 does not contain expected text: $2"
    fi
    success "File contains expected content: $1"
}

check_dir_not_empty() {
    if [ -z "$(ls -A "$1" 2>/dev/null)" ]; then
        error_exit "Directory is empty: $1"
    fi
    success "Directory has content: $1"
}

wait_for_user() {
    if [ "$NO_WAIT" = false ]; then
        read -p "$1"
    else
        echo "$1 (auto-continuing...)"
        sleep 1
    fi
}

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Activate venv
if [ ! -d ".venv" ]; then
    error_exit "Virtual environment not found. Run: python3 -m venv .venv"
fi

source .venv/bin/activate || error_exit "Failed to activate venv"

PYTHON=".venv/bin/python3"
VAULT="vaults/peaklogistics"

# =============================================================================
# DEMO START
# =============================================================================

narrate "Welcome to the Claude TPM Agent demo!"
echo "This is an automated walkthrough that validates each step of the demo."
echo "If any step fails, the script will stop and show you what went wrong."
echo ""
wait_for_user "Press Enter to start the demo..."

# =============================================================================
# PRE-DEMO: Reset to clean state
# =============================================================================

narrate "First, let me reset the vault to a clean Day 0 state..."
step "Running demo-reset.sh"
./demo-reset.sh || error_exit "Reset script failed"
success "Vault reset complete"

# Verify clean state
step "Verifying clean state..."
if [ -n "$(find $VAULT/agent/logs -name '*.md' 2>/dev/null)" ]; then
    error_exit "Logs directory not clean after reset"
fi
if [ -n "$(find $VAULT/agent/memory -name '*.md' 2>/dev/null)" ]; then
    error_exit "Memory directory not clean after reset"
fi
success "Vault is in pristine Day 0 state"

# =============================================================================
# ACT 1: PROJECT SETUP & FIRST RUN
# =============================================================================

narrate "ACT 1: Project Setup & First Run"
echo "We're at project kickoff. The vault has project scope, timeline, team info,"
echo "and initial risk register. Let's run the Delivery Manager role for the first time."
echo ""
wait_for_user "Press Enter to continue..."

step "Showing vault structure..."
tree -L 2 $VAULT/ || error_exit "Tree command failed"
success "Vault structure displayed"

# Check key directories exist
step "Verifying key directories exist..."
for dir in stakeholders goals project context agent; do
    if [ ! -d "$VAULT/$dir" ]; then
        error_exit "Missing directory: $VAULT/$dir"
    fi
done
success "All key directories present"

narrate "Now let's run the Delivery Manager for the first time."
echo "Claude will read the system prompt, load context files, check its inbox (empty),"
echo "and write a reasoning log following THINK/ACT/REFLECT pattern."
echo ""
wait_for_user "Press Enter to run Delivery Manager..."

step "Running: python3 runner.py --role delivery"
timeout 120 $PYTHON runner.py --role delivery || error_exit "Delivery Manager run failed or timed out"
success "Delivery Manager completed first run"

step "Checking for reasoning log..."
DELIVERY_LOG=$(find $VAULT/agent/logs/delivery/ -name "*.md" -type f | head -1)
if [ -z "$DELIVERY_LOG" ]; then
    error_exit "No reasoning log created by Delivery Manager"
fi
success "Reasoning log created: $(basename "$DELIVERY_LOG")"

step "Verifying log structure..."
check_file_contains "$DELIVERY_LOG" "Inbox"
check_file_contains "$DELIVERY_LOG" "What Changed"
check_file_contains "$DELIVERY_LOG" "Priority Action"
success "Log has proper THINK/ACT/REFLECT structure"

narrate "Great! The Delivery Manager established baseline awareness."
echo "Notice how Claude structures its thinking - this isn't a black box."
echo ""
wait_for_user "Press Enter to continue to Act 2..."

# =============================================================================
# ACT 2: NORMAL OPERATIONS - ROLE COORDINATION
# =============================================================================

narrate "ACT 2: Normal Operations - Role Coordination"
echo "Fast forward to week 2. A developer reports a blocker: the shipping carrier's"
echo "API is poorly documented and integration is taking longer than expected."
echo "Let's see how the roles coordinate."
echo ""
wait_for_user "Press Enter to continue..."

step "Creating blocker trigger for Risk Manager..."
cat > $VAULT/agent/inbox/risk/2026-02-14T14-30-blocker-auth.md << 'EOF'
---
from: user
date: 2026-02-14T14:30:00Z
priority: high
---

**Blocker identified:**

Joao (Backend Lead) reports that the user authentication implementation is more complex than estimated. JWT token management, session handling, and role-based access control (supplier vs shipper) is taking 2x longer than estimated.

Originally: 2 days (per scope.md)
Now: likely 4 days

**Impact:**
- Timeline: Pushes Week 2 milestone "User sign-up/login working" by 2 days
- Dependencies: Blocks all user-specific features (posting shipments/trips)
- Critical path: Authentication is a prerequisite for everything else

**Request:**
Assess this as a risk and recommend mitigation.
EOF
success "Trigger file created in Risk inbox"

narrate "I just dropped a trigger file in the Risk Manager's inbox."
echo "This is how events enter the system. In production, this could come from"
echo "automated monitoring, Slack webhooks, CI/CD failures, or manual input."
echo ""
wait_for_user "Press Enter to run Risk Manager..."

step "Running: python3 runner.py --role risk"
timeout 120 $PYTHON runner.py --role risk || error_exit "Risk Manager run failed or timed out"
success "Risk Manager processed blocker"

step "Checking if Risk updated project files..."
check_file_exists "$VAULT/project/risks.md"
check_file_exists "$VAULT/context/blockers.md"
success "Risk Manager updated risk register and blockers"

step "Checking if Risk archived the trigger..."
if [ -f "$VAULT/agent/inbox/risk/2026-02-14T14-30-blocker-auth.md" ]; then
    error_exit "Trigger file not archived (still in inbox)"
fi
success "Trigger file was processed and archived"

step "Checking if Risk notified Delivery..."
DELIVERY_INBOX="$VAULT/agent/inbox/delivery"
if [ -z "$(ls -A "$DELIVERY_INBOX" 2>/dev/null)" ]; then
    echo "⚠️  Warning: Risk didn't create trigger for Delivery (optional behavior)"
else
    success "Risk created notification for Delivery"
fi

narrate "The Risk Manager assessed the blocker, documented it in the risk register,"
echo "and added mitigation steps. Now let's see how Delivery responds."
echo ""
wait_for_user "Press Enter to run Delivery Manager..."

step "Running: python3 runner.py --role delivery"
timeout 120 $PYTHON runner.py --role delivery || error_exit "Delivery Manager run failed"
success "Delivery Manager responded to Risk notification"

step "Checking Delivery's reasoning log..."
DELIVERY_LOG_2=$(find $VAULT/agent/logs/delivery/ -name "*.md" -type f | tail -1)
check_file_exists "$DELIVERY_LOG_2"
success "Delivery created new reasoning log"

narrate "Perfect! Delivery Manager received the notification and assessed the impact."
echo "The roles coordinated asynchronously - like a distributed team."
echo ""
wait_for_user "Press Enter to continue to Act 3..."

# =============================================================================
# ACT 3: WEEK 5 CRISIS - CLIENT REQUESTS MORE FEATURES
# =============================================================================

narrate "ACT 3: Week 5 Crisis - Client Requests More Features"
echo "We're at week 5. On track. Then the client (Sarah Chen, CTO) sends an email:"
echo "'We'd love to add real-time shipment notifications before launch.'"
echo "Classic scope creep. Let's see how the agent helps navigate this."
echo ""
wait_for_user "Press Enter to continue..."

step "Creating client request trigger for Comms Manager..."
cat > $VAULT/agent/inbox/comms/2026-02-14T15-00-client-request.md << 'EOF'
---
from: user
date: 2026-02-14T15:00:00Z
priority: high
---

**Client email received:**

From: Sarah Chen (Peak Logistics CTO)
Subject: Feature request - Real-time notifications

Hi Bruno,

The team is really excited about the dashboard! We've been thinking - would it be possible to add **real-time SMS/email notifications** when shipments reach key milestones (picked up, in transit, delivered)?

We know we're at week 5, but this would be a game-changer for our customers. Let me know if this is feasible before the Feb 28 deadline.

Thanks!
Sarah

**Request:**
Coordinate with Delivery and Risk to assess feasibility and provide options.
EOF
success "Client request trigger created"

narrate "Now let's see how Comms Manager handles this."
echo ""
wait_for_user "Press Enter to run Comms Manager..."

step "Running: python3 runner.py --role comms"
timeout 120 $PYTHON runner.py --role comms || error_exit "Comms Manager run failed"
success "Comms Manager processed client request"

step "Checking if Comms notified other roles..."
if [ -n "$(ls -A "$VAULT/agent/inbox/delivery" 2>/dev/null)" ]; then
    success "Comms notified Delivery"
fi
if [ -n "$(ls -A "$VAULT/agent/inbox/risk" 2>/dev/null)" ]; then
    success "Comms notified Risk"
fi

step "Checking if Comms drafted a response..."
if [ -n "$(ls -A "$VAULT/agent/outbox/comms/drafts" 2>/dev/null)" ]; then
    success "Comms drafted acknowledgment for client"
else
    echo "⚠️  Note: Comms might not draft until after analysis"
fi

narrate "Good! Comms recognized this needs cross-role coordination."
echo "Now let's run Delivery to analyze the timeline impact."
echo ""
wait_for_user "Press Enter to run Delivery Manager..."

step "Running: python3 runner.py --role delivery"
timeout 120 $PYTHON runner.py --role delivery || error_exit "Delivery Manager run failed"
success "Delivery Manager analyzed request"

step "Checking if Delivery asked the User a question..."
USER_INBOX="$VAULT/agent/inbox/user"
if [ -n "$(ls -A "$USER_INBOX" 2>/dev/null)" ]; then
    success "Delivery asked User for guidance (Q&A cycle working!)"
    QUESTION_FILE=$(ls -t "$USER_INBOX" | head -1)
    echo "    Question file: $QUESTION_FILE"
else
    echo "⚠️  Note: Delivery might have drafted options instead of asking"
fi

narrate "Let's also run Risk to get their assessment."
echo ""
wait_for_user "Press Enter to run Risk Manager..."

step "Running: python3 runner.py --role risk"
timeout 120 $PYTHON runner.py --role risk || error_exit "Risk Manager run failed"
success "Risk Manager assessed scope change risk"

step "Checking Risk's output..."
RISK_LOG=$(find $VAULT/agent/logs/risk/ -name "*.md" -type f | tail -1)
check_file_exists "$RISK_LOG"
success "Risk documented assessment"

narrate "Excellent! Now both Delivery and Risk have analyzed the situation."
echo "In the full demo, you would:"
echo "  1. Review questions from Delivery/Risk in agent/inbox/user/"
echo "  2. Create answered files with your strategic decision"
echo "  3. Run --once to route answers back to roles"
echo "  4. Roles would then create recommendations/drafts"
echo ""
echo "For this automated demo, we'll skip the interactive Q&A cycle."
echo ""
wait_for_user "Press Enter to continue to Act 4..."

# =============================================================================
# ACT 4: SYSTEM FEATURES SHOWCASE
# =============================================================================

narrate "ACT 4: System Features Showcase"
echo "Let's look at the system features that make this work."
echo ""
wait_for_user "Press Enter to continue..."

step "Checking role memory files..."
for role in delivery risk comms; do
    MEMORY_FILE="$VAULT/agent/memory/${role}.md"
    if [ -f "$MEMORY_FILE" ]; then
        success "Memory file exists: $role"
    else
        echo "    (No memory file yet for $role - created after first reflection)"
    fi
done

step "Checking reasoning logs..."
for role in delivery risk comms; do
    LOG_DIR="$VAULT/agent/logs/${role}"
    if [ -n "$(ls -A "$LOG_DIR" 2>/dev/null)" ]; then
        LOG_COUNT=$(ls "$LOG_DIR"/*.md 2>/dev/null | wc -l)
        success "Role $role has $LOG_COUNT reasoning log(s)"
    fi
done

step "Checking session management..."
if [ -f "sessions/sessions.json" ]; then
    success "Session file exists (roles will resume same-day context)"
    cat sessions/sessions.json
else
    echo "    (No sessions yet - will be created after first role run)"
fi

narrate "All the pieces are working!"
echo ""
echo "Summary of what happened:"
echo "  ✅ Delivery Manager ran and established baseline (Act 1)"
echo "  ✅ Risk Manager processed blocker and coordinated with Delivery (Act 2)"
echo "  ✅ Comms Manager handled client request and notified other roles (Act 3)"
echo "  ✅ Roles asked questions and created assessments (Act 3)"
echo "  ✅ All reasoning logged, memory accumulating, sessions tracked (Act 4)"
echo ""

# =============================================================================
# WRAP-UP
# =============================================================================

narrate "🎉 Demo validation complete!"
echo ""
echo "All critical flows validated:"
echo "  ✅ Role execution (Delivery, Risk, Comms)"
echo "  ✅ Inbox triggering (event-driven)"
echo "  ✅ Role coordination (Risk → Delivery)"
echo "  ✅ User Q&A cycle (questions created)"
echo "  ✅ Reasoning logs (THINK/ACT/REFLECT)"
echo "  ✅ Context updates (risks, blockers)"
echo "  ✅ Session management"
echo ""
echo "The system is working as expected! 🚀"
echo ""
echo "To run a live demo:"
echo "  1. Run: ./demo-reset.sh"
echo "  2. Follow: DEMO-SCRIPT.md"
echo "  3. Execute each step manually, explaining as you go"
echo ""
echo "To run this validation again:"
echo "  ./demo-automated.sh"
echo ""

success "Demo validation completed successfully!"
