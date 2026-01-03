# Task Terminal (tt)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> A local-first developer tool for generating and tracking task IDs that seamlessly link to GitHub PRs.

Task Terminal (tt) is a polished terminal application that helps developers maintain a monotonically increasing, globally unique sequence of task IDs across all their projects, with automatic GitHub PR detection and linking.

## ✨ Features

- 🎯 **Global Task IDs** - Monotonically increasing IDs (tt-1, tt-2, tt-3...) that never reset
- 💾 **Local SQLite Storage** - All data stored locally in `~/.tt/tasks.db`
- 🔗 **GitHub PR Integration** - Automatic detection and linking of PRs via GitHub CLI
- 🚀 **Cross-Project** - One global sequence across all your repositories
- 🔍 **PR Management** - View, link, and open PRs directly from the terminal

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- [GitHub CLI](https://cli.github.com/) (optional, for PR features)

### Install from PyPI

```bash
pip install task-terminal
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install task-terminal
```

### Setup GitHub CLI (Optional)

For PR detection and linking features:

```bash
# Windows
winget install --id GitHub.cli

# macOS
brew install gh

# Authenticate
gh auth login
```

## Quick Start

1. **Install Task Terminal**

   ```bash
   pip install task-terminal
   ```

2. **Launch the application**

   ```bash
   tt
   ```

   If `tt` command is not found, try:
   ```bash
   python -m tt.main
   ```

3. **Navigate to your project (for PR features)**

   ```bash
   cd ~/projects/your-repo
   tt
   ```

4. **Create your first task**
   - Navigate to "Create Task" with arrow keys
   - Press Enter to generate a task ID
   - The ID (e.g., `tt-1`) is copied to your clipboard

5. **Use the task ID in your workflow**

   ```bash
   git checkout -b feature/tt-1-implement-auth
   # Make your changes
   git push origin feature/tt-1-implement-auth
   ```

6. **Import and link PRs**
   - Create a PR on GitHub with tt-1 in the branch name or title
   - Open tt and navigate to "PR Inbox"
   - Press 'l' or Enter on tt-1 to import and link the PR

## 📖 Usage Guide

### Main Menu

Navigate with **arrow keys** and select with **Enter**:

- **Create Task** - Generate a new task ID
- **Tasks** - View all tasks and their status
- **PR Inbox** - Detect and link PRs to tasks
- **Settings** - Coming soon
- **Quit** - Exit the application

**Shortcuts:** `q` or `Escape` to quit

### Create Task Screen

**Shortcuts:**

- `Enter` - Generate a new task ID
- `Escape` - Go back to main menu

The generated task ID is automatically copied to your clipboard for immediate use.

### Tasks Screen

View all your tasks with their status, creation date, and linked PRs.

**Shortcuts:**

- `Arrow keys` - Navigate tasks
- `d` - Delete the highlighted task
- `o` - Open the linked PR in your browser
- `r` - Refresh the task list
- `Escape` - Go back to main menu

### PR Inbox Screen

Automatically scans for PRs in the current repository and detects task IDs in branch names and PR titles.

**Features:**
- **Import** - Task IDs found in the repo but not in your local database
- **Link** - PRs for existing tasks that need to be linked

**Shortcuts:**

- `Arrow keys` - Navigate items
- `Enter` or `l` - Link PR or import task ID
- `i` - Ignore the highlighted item (session only)
- `r` - Refresh and rescan the repository
- `Escape` - Go back to main menu

## 🎯 Workflow Example

```bash
# 1. Install Task Terminal
pip install task-terminal

# 2. Generate a task ID
tt
# Navigate to "Create Task", press Enter
# Result: tt-42 (copied to clipboard)

# 3. Navigate to your project and create a branch
cd ~/projects/my-api
git checkout -b feature/tt-42-add-authentication

# 4. Implement your feature
# ... make changes ...
git add .
git commit -m "Add JWT authentication for API"
git push origin feature/tt-42-add-authentication

# 5. Create a PR on GitHub (with task ID in title or branch)
gh pr create --title "tt-42: Add authentication" --body "Implements JWT auth"

# 6. Import and link the task in tt
tt
# Navigate to "PR Inbox"
# You'll see "Import | tt-42 | #123 | Add authentication"
# Press 'l' or Enter to import and link

# 7. View your tasks
# Navigate to "Tasks"
# See tt-42 status: linked, with PR #123 and title
# Press 'o' to open the PR in your browser
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/sumanthaka/TerminalTask.git
cd TerminalTask

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Run from Source

```bash
tt
```

### Code Style

```bash
# Format code
ruff format
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Textual](https://github.com/Textualize/textual) - An amazing TUI framework
- Inspired by the need for simple, local-first developer tools
- GitHub CLI integration powered by [gh](https://cli.github.com/)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/sumanthaka/TerminalTask/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sumanthaka/TerminalTask/discussions)

## 🗺️ Roadmap

- [ ] Task search and filtering
- [ ] Export tasks to JSON/CSV
- [ ] Multi-PR support per task

---
