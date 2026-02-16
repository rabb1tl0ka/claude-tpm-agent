# Currents state
- Role creates trigger file in agent/inbox/delivery/blocker-xyz.md
- File sits there until... scheduler polls 60 seconds later
- Or you manually run python3 runner.py --once                                 

# The problem:
  1. Latency — Up to 60 seconds before the system reacts to events
  2. Demo perception — You're manually running roles, breaking the "autonomous agent" illusion
  3. Inefficiency — Scheduler wakes up every 60s to check "anything new?" (wasteful)

# Solution: File System Watcher

  Use inotify (Linux) / FSEvents (macOS) / ReadDirectoryChangesW (Windows) to watch inbox directories
  and trigger roles immediately when files appear.

# Implementation approach:
```
  import asyncio
  from watchdog import observers, events  # Python library for cross-platform file watching

  class InboxHandler(events.FileSystemEventHandler):
      def on_created(self, event):
          if event.is_directory or not event.src_path.endswith('.md'):
              return

          # Parse which role owns this inbox
          # /path/to/agent/inbox/delivery/file.md -> role="delivery"
          role_name = extract_role_from_path(event.src_path)

          log.info(f"[inbox-watcher] New file: {event.src_path} → triggering {role_name}")

          # Trigger role run immediately (async)
          asyncio.create_task(run_role_async(role_name, "inbox trigger"))
```

#Changes needed:

  1. Add watchdog dependency to requirements.txt
  2. Start file watcher thread in main() alongside the scheduler
  3. Watch all role inboxes (agent/inbox/delivery/, agent/inbox/risk/, etc.)
  4. Debounce rapid triggers (if 3 files created in 1 second, run role once, not 3x)
  5. Watch user/answered/ too for Q&A routing

# Demo impact:

  Before (current):
  You: "Let me manually trigger Risk Manager..." [types command]
  Audience: 🤨 "You're just running Python scripts..."

  After (with file watcher):
  You: "Watch what happens when I drop a blocker in Risk's inbox..." [creates file]
  [2 seconds later]
  Risk Manager: [starts reasoning, visible in tail window]
  Audience: 😮 "Oh damn, it just REACTED to that!"

# Additional benefits:

  - No polling overhead — System is idle until events happen
  - Sub-second response — Roles react in 100-500ms, not 60s
  - True event-driven architecture — Matches how you described it in the A
