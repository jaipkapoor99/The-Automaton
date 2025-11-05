# The Automaton

**The Automaton** is a powerful, extensible framework for automating the
collection, synchronization, and management of your personal data from various
online platforms.

## Features

- **Modular Architecture**: Easily extend the framework by adding new modules
  for different services.
- **Profile Generation**: Automatically generate detailed profiles from
  services like Codeforces, LeetCode, Chess.com, Steam, and YouTube.
- **Cloud Sync**: Synchronize your data to a single Google Sheet (with separate subsheets for each platform's data) and a configurable local directory.
- **Command-Line Interface**: A simple and intuitive CLI for running
  workflows directly via Python scripts.
- **Customizable**: Configure the tool to your needs using a central
  `config.yaml` and a `.env` file for sensitive data.

## Setup

For detailed instructions on how to set up and configure The Automaton, please
see the [Setup Guide](SETUP.md).

## Usage

All workflows are run directly through the `main.py` script in the `scripts`
directory. To see a list of available workflows, examine `scripts/main.py`.

To run a specific workflow, use:

```bash
python3 scripts/main.py [workflow_name]
```

For example, to generate a Codeforces profile:

```bash
python3 scripts/main.py generate-codeforces
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with
your proposed changes.

## License

This project is licensed under the MIT License.
