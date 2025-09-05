# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-09-05

### Added

- **Bash Workflow**: Introduced `workflow.sh` as a bash alternative to the
  PowerShell script for running workflows.

### Changed

- **Google OAuth Flow**: Refactored the Google Authentication process from an
  automated local server to a manual, file-based flow. This allows for
  authentication in environments without a local web server.
- **Updated Documentation**: Updated `README.md` and `SETUP.md` to reflect
  the new authentication process and the addition of the bash workflow.

## [1.0.0] - 2025-09-01

### Added

- **Initial Release**: First public version of The Automaton.
- **Profile Generation**: Added modules to generate user profiles for
    Codeforces, LeetCode, Steam, YouTube, and Chess.com.
- **Cloud Synchronization**: Implemented functionality to sync generated
    profiles to Google Docs and a local directory.
- **Configuration Management**: Centralized all configuration into
    `config.yaml` and a `.env` file for sensitive data.
- **Workflow Automation**: Created a PowerShell script (`workflow.ps1`) to
    orchestrate all tasks and a Python script (`main.py`) to execute them.
- **Modular Architecture**: Designed the project with a modular structure to
    allow for easy extension and maintenance.

### Changed

- **Refactored for General Use**: Adapted the project from a personal script
    into a generalized, reusable framework.
- **Improved Robustness**: Made file paths and API endpoints configurable,
    and improved error handling throughout the application.
- **Consolidated Code**: Merged all profile generator classes into a single,
    cohesive module.

### Removed

- **Resume Builder**: Removed all functionality related to building and
    syncing a resume.
- **File Concatenation**: Removed the file concatenation feature to focus on
    core API interactions.
- **PC Specs Module**: Deleted the module for syncing PC specifications.
