"""Config — vault path + role config parser.

Role configs are Markdown files in roles/ with structured sections.
The parser extracts model, mission, goals, context files, tools, schedule, and inbox path.
"""

import os
import re
from dotenv import load_dotenv

load_dotenv()

# Vault — default is relative to this file's directory, not cwd
_DEFAULT_VAULT = os.path.join(os.path.dirname(__file__), "vaults", "peaklogistics")
VAULT_PATH = os.path.expanduser(os.environ.get("VAULT_PATH", _DEFAULT_VAULT))

# Roles directory (sibling to this file)
ROLES_DIR = os.path.join(os.path.dirname(__file__), "roles")

# Session tracking directory
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), ".sessions")


# ---------------------------------------------------------------------------
# Role config parser
# ---------------------------------------------------------------------------

def _parse_sections(text: str) -> dict[str, str]:
    """Split a Markdown file into {section_name: content} by ## headers."""
    sections = {}
    current = None
    lines = []
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+)$", line)
        if match:
            if current is not None:
                sections[current] = "\n".join(lines).strip()
            current = match.group(1).strip().lower()
            lines = []
        elif current is not None:
            lines.append(line)
    if current is not None:
        sections[current] = "\n".join(lines).strip()
    return sections


def _parse_bullet_list(text: str) -> list[str]:
    """Extract items from a Markdown bullet list."""
    items = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip())
    return items


def _parse_title(text: str) -> str:
    """Extract the # title from a Markdown file."""
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+)$", line)
        if match:
            return match.group(1).strip()
    return ""


def load_role(role_name: str) -> dict:
    """Load and parse a role config from roles/<role_name>.md.

    Returns a dict with keys:
        name, display_name, model, mission, goals, context_files,
        tools, schedule, inbox, preferences
    """
    path = os.path.join(ROLES_DIR, f"{role_name}.md")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Role config not found: {path}")

    with open(path) as f:
        text = f.read()

    sections = _parse_sections(text)

    return {
        "name": role_name,
        "display_name": _parse_title(text),
        "model": sections.get("model", "sonnet").strip(),
        "mission": sections.get("mission", ""),
        "goals": _parse_bullet_list(sections.get("goals", "")),
        "context_files": _parse_bullet_list(sections.get("context files", "")),
        "tools": _parse_bullet_list(sections.get("tools", "")),
        "schedule": sections.get("schedule", ""),
        "inbox": sections.get("inbox", "").strip(),
        "preferences": sections.get("user preferences", ""),
    }


def list_roles() -> list[str]:
    """Return names of all available roles (from .md files in roles/)."""
    if not os.path.isdir(ROLES_DIR):
        return []
    return sorted(
        os.path.splitext(f)[0]
        for f in os.listdir(ROLES_DIR)
        if f.endswith(".md")
    )
