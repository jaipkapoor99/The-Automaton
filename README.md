# The Automaton

**The Automaton** is a powerful, extensible framework for automating the
collection, synchronization, and management of your personal data from various
online platforms.

## Features

- **Modular Architecture**: Easily extend the framework by adding new modules
    for different services.
- **Profile Generation**: Automatically generate detailed profiles from
    services like Codeforces, LeetCode, Chess.com, Steam, and YouTube.
- **Cloud Sync**: Synchronize your data to Google Docs and a configurable
    local directory.
- **Command-Line Interface**: A simple and intuitive CLI for running
    workflows via a PowerShell script.
- **Customizable**: Configure the tool to your needs using a central
    `config.yaml` and a `.env` file for sensitive data.

## Setup

For detailed instructions on how to set up and configure The Automaton, please
see the [Setup Guide](SETUP.md).

## Usage

All workflows are run through the `workflow.sh` script in the `scripts`
directory. To see a list of all available actions, run:

```bash
./scripts/workflow.sh -Action help
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with
your proposed changes.

## License

This project is licensed under the MIT License.
