# The Automaton

**The Automaton** is a powerful, extensible framework for automating the
collection, synchronization, and management of your personal data from various
online platforms. Originally a personal project, it has been generalized to
serve as a reusable tool for any developer looking to create a centralized hub
for their digital life.

## Features

- **Modular Architecture**: Easily extend the framework by adding new modules
  for different services.
- **Profile Generation**: Automatically generate detailed profiles from services
  like:
  - Codeforces
  - LeetCode
  - Chess.com
  - Steam
  - YouTube
- **Cloud Sync**: Synchronize your data to Google Docs, Google Drive, and local
  storage (e.g., OneDrive).
- **Command-Line Interface**: A simple and intuitive CLI for running workflows,
  generating profiles, and syncing data.
- **Customizable**: Configure the tool to your needs using a simple `.env`
  file.

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- PowerShell (for the workflow script)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/The-Automaton.git
    cd The-Automaton
    ```

2. **Install Python dependencies:**

    ```bash
    pip install -r scripts/requirements.txt
    ```

### Configuration

1. **Create a `.env` file:**
    Copy the `.env.example` file to a new file named `.env`.

    ```bash
    cp .env.example .env
    ```

2. **Fill in your credentials:**
    Open the `.env` file and fill in your API keys, user IDs, and other
    configuration variables.

## Usage

The main entry point for all workflows is the `workflow.ps1` script.

### Actions

- **`run`**: Run the full, default workflow (generate all, sync all,
  commit).
- **`generate`**: Generate specific profile data.
- **`sync`**: Sync data to local or cloud services.
- **`validate`**: Run validation scripts.
- **`help`**: Show the help message.

### Services

- **`all`**: Target all services.
- **`codeforces`**: Target Codeforces.
- **`leetcode`**: Target LeetCode.
- **`steam`**: Target Steam.
- **`youtube`**: Target YouTube.
- **`chess-com`**: Target Chess.com.
- **`books`**: Target book synchronization.
- **`local`**: Target local file sync.
- **`cloud`**: Target cloud synchronization.

### Examples

- **Run the full workflow:**

    ```powershell
    .\scripts\workflow.ps1 run -CommitMessage "feat: update profiles and sync data"
    ```

- **Generate only the Codeforces profile:**

    ```powershell
    .\scripts\workflow.ps1 generate -Service codeforces
    ```

- **Sync all data to the cloud:**

    ```powershell
    .\scripts\workflow.ps1 sync -Service cloud
    ```

## Contributing

Contributions are welcome! Please read the `CONTRIBUTING.md` file for details
on how to contribute to the project.

## License

This project is licensed under the MIT License. See the `LICENSE` file for
details.
