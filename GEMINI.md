# Gemini Memories

- This project, named "The-Automaton", uses a modular architecture with Python scripts orchestrated by a PowerShell workflow (`workflow.ps1`) and a shell script (`workflow.sh`).
- The primary goal is to automate the collection and synchronization of user data from various online platforms. This includes:
  - **Profile Generation**: Automatically generating detailed profiles from services such as Codeforces, LeetCode, Chess.com, Steam, and YouTube.
  - **Cloud Synchronization**: Synchronizing collected data to a single Google Sheet (with separate subsheets for each platform's data) and a configurable local directory.
  - **AI Integration**: Utilizing Perplexity AI for potential data processing or summarization tasks.
- Configuration is managed through `config.yaml` for general settings (e.g., API endpoints, file paths) and `.env` for sensitive data. The `GOOGLE_SHEET_ID` is now the single source of truth for Google Sheet synchronization.
- Code quality is maintained using `black` for formatting, `isort` for import sorting, `autoflake` for removing unused imports, and `pylint` for linting.
- The user prefers clear, concise commit messages that follow conventional formats.
- Fall back on MCP servers as much as possible.
- **Git and Workflow Commands**: The Gemini CLI should NOT run any `git` commands or workflow commands (e.g., `workflow.sh`, `workflow.ps1`). The user handles these operations exclusively via the VS Code GUI.
- **Type Checking**: Proper type checking and type hints are essential, even if it means being pedantic. Ensure all functions and variables have appropriate type annotations.
