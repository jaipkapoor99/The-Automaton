# Claude Memories

- This project, named "The-Automaton", uses a modular architecture with Python scripts orchestrated by a PowerShell workflow (`workflow.ps1`) and a shell script (`workflow.sh`).
- The primary goal is to automate the collection and synchronization of user data from various online platforms. This includes:
  - **Profile Generation**: Automatically generating detailed profiles from services such as Codeforces, LeetCode, Chess.com, Steam, and YouTube.
  - **Cloud Synchronization**: Synchronizing collected data to Google Docs and a configurable local directory.
  - **AI Integration**: Utilizing Perplexity AI for potential data processing or summarization tasks.
- Configuration is managed through `config.yaml` for general settings (e.g., API endpoints, file paths) and `.env` for sensitive data.
- The user prefers clear, concise commit messages that follow conventional formats.