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

### Install from Source

```bash
git clone https://github.com/yourusername/TerminalTask.git
cd TerminalTask
pip install -e .
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

1. **Install tt globally**

   ```bash
   pip install -e .
   ```

2. **Navigate to your project**

   ```bash
   cd ~/projects/your-repo
   ```

3. **Launch Task Terminal**

   ```bash
   tt
   ```

4. **Create your first task**
   - Navigate to "Create Task" with arrow keys
   - Press Enter or 'g' to generate a task ID
   - The ID (e.g., `tt-1`) is copied to your clipboard

5. **Use the task ID in your workflow**

   ```bash
   git checkout -b feature/tt-1-implement-auth
   # Make your changes
   git push origin feature/tt-1-implement-auth
   ```

6. **Link the PR**
   - Create a PR on GitHub
   - Open tt and navigate to "PR Inbox"
   - Select your PR and press Enter or 'a' to attach

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

- `Enter` or `g` - Generate a new task ID
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

Automatically scans for PRs in the current repository that match your open task IDs.

**Shortcuts:**

- `Arrow keys` - Navigate PRs
- `Enter` or `a` - Attach highlighted PR to its task
- `i` - Ignore the highlighted PR (session only)
- `r` - Refresh and rescan for PRs
- `Escape` - Go back to main menu

## 🎯 Workflow Example

```bash
# 1. Start in your project directory
cd ~/projects/my-api

# 2. Generate a task ID
tt
# Navigate to "Create Task", press Enter
# Result: tt-42 (copied to clipboard)

# 3. Create a branch with the task ID
git checkout -b feature/tt-42-add-authentication

# 4. Implement your feature
# ... make changes ...
git add .
git commit -m "Add JWT authentication for API"
git push origin feature/tt-42-add-authentication

# 5. Create a PR on GitHub
gh pr create --title "tt-42: Add authentication" --body "Implements JWT auth"

# 6. Link the PR in tt
tt
# Navigate to "PR Inbox"
# Select the PR with arrow keys
# Press Enter to attach

# 7. View your tasks
# Navigate to "Tasks"
# See tt-42 status: linked, with PR #123
# Press 'o' to open the PR in your browser
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/suamnthaka/TerminalTask.git
cd TerminalTask

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
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
