# Copilot Instructions — Task Terminal (tt)

## Project Status
🚧 **Early Stage Development** — Core implementation in progress.

## What tt Is

A local-first developer tool for generating and tracking task IDs that later attach to GitHub PRs.

**What it is NOT:**
- A project management tool
- A git automation tool  
- A cloud-based service

**What it IS:**
- A task ID terminal with a polished TUI
- A keyboard-first, local-only tool
- A power tool for explicit, manual workflows

## Implementation Philosophy

Implement features **faithfully and literally** as described below.
- Do not simplify into a script
- Do not over-engineer into a platform
- Respect explicitness over magic
- Respect polish over minimalism
- Respect local-first over integrations

---

## Core Concept

- `tt` generates **monotonically increasing task IDs** like:
  - tt-1, tt-2, tt-3, ...
- IDs are **local**, **persistent**, and stored in SQLite.
- The tool is **independent of git workflow**:
- It does NOT switch branches
- It does NOT create branches
- It does NOT rename branches
- The user manually uses the generated ID in a branch name.
- Later, when a GitHub PR exists with that ID in the branch name or title,
`tt` can **pull the PR title and description** and attach it to the task.

---

## UX Principles (Very Important)

- This tool must NOT feel minimal or script-like.
- It must feel like a **real terminal application** with:
- buttons
- focus states
- arrow-key navigation
- Keyboard-first, mouse-optional.
- Explicit actions only (no hidden automation).

Use a **TUI framework** (preferably `textual`).

---

## Required Screens (TUI)

### 1. Main Menu

A navigable menu with arrow keys:

- **Create Task**
- **Tasks**
- **PR Inbox**
- **Settings** (can be stubbed)

There must be a visible "button" or highlighted selection.
No single-command CLI-only flow.

---

### 2. Create Task Screen

When user selects **Create Task**:

1. Generate the next ID: `tt-<number>`
2. Persist it in SQLite
3. Copy the ID to the system clipboard
4. Show visual confirmation

**Example flow:**
```
Generated: tt-123
Copied to clipboard ✓

[Back to Menu]
```

Do NOT:
- ask for title
- ask for description
- interact with git

---

### 3. Tasks Screen

Display a list of tasks:

| ID     | Status | Created            | PR  |
|--------|--------|--------------------|-----|
| tt-123 | linked | 2026-01-01 10:30am | #45 |
| tt-122 | open   | 2026-01-01 09:15am | -   |

Read-only in v1. Arrow-key navigation optional.

---

### 4. PR Inbox Screen

This screen:
- Detects GitHub PRs that reference a task ID
- Shows unlinked PRs
- Allows user to explicitly attach PR metadata to a task

**UI example:**
```
Found PR: tt-123
Branch: feature/tt-123-implement-auth
Title: Implement authentication flow

[Attach to task] [Ignore]
```

On attach:
- Save PR number, title, body
- Mark task as linked
- Show confirmation

---

## Data Storage (SQLite)

Use SQLite for persistence.

### Tables

#### `tasks`
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,        -- e.g. 'tt-123'
    status TEXT NOT NULL,              -- 'open' or 'linked'
    created_at DATETIME NOT NULL
);
```

#### `prs`
```sql
CREATE TABLE prs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_code TEXT NOT NULL,
    repo TEXT NOT NULL,
    pr_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (task_code) REFERENCES tasks(code)
);
```

**Important:** IDs must be **monotonic and never reused**.

---

## GitHub Integration

- Use GitHub CLI (`gh`) or GitHub API
- PR detection should:
  - Match task ID in branch name or PR title
  - Use patterns like: `tt-\d+`
- PR syncing is **manual**, triggered from the UI
- Never rename PRs
- Never modify branches

---

## What NOT To Build (Hard Constraints)

DO NOT:
- Implement kanban boards
- Auto-create or switch git branches
- Enforce semantic naming
- Add cloud sync
- Add auth or accounts
- Infer intent automatically
- Add config files in v1

---

## Suggested Project Structure

```
tt/
├── tt/
│   ├── core/
│   │   ├── ids.py          # Task ID generation logic
│   │   └── tasks.py        # Task business logic
│   ├── infra/
│   │   ├── sqlite.py       # Database access layer
│   │   └── github.py       # GitHub CLI/API integration
│   ├── tui/
│   │   ├── app.py          # Main Textual app
│   │   └── screens/        # TUI screens (menu, tasks, pr_inbox)
│   └── main.py             # Entry point
├── tests/                   # Unit and integration tests
├── pyproject.toml          # Dependencies (textual, rich, etc.)
└── README.md
```

**Separation of concerns:**
- UI logic isolated from data logic
- SQLite access isolated in infra layer
- GitHub logic isolated in infra layer

---

## Tech Stack

**TUI Framework:** `textual` (required)
- Provides buttons, focus states, arrow-key navigation
- Keyboard-first, mouse-optional UX

**Database:** SQLite
- Local persistence only
- Monotonically increasing task IDs

**GitHub Integration:** `gh` CLI or GitHub API
- Manual PR detection and syncing only
- Never modify branches or PRs

---

## Development Workflow

### Setup (when implemented)
```powershell
# Install dependencies
pip install -e .

# Run app
python -m tt
# or
tt
```

### Testing (when implemented)
```powershell
pytest tests/
```

---

## Quality Bar

- The app should be pleasant to open repeatedly
- The UI must feel intentional
- No placeholder text like "TODO screen"
- Errors should be visible and human-readable

---

## Final Reminder

This is a **personal power tool for a senior engineer**.
Respect explicitness over magic.
Respect polish over minimalism.
Respect local-first over integrations.

Build the tool described — not a simpler or larger one.
