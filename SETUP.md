# The Automaton Setup Guide

This guide provides detailed instructions for setting up and configuring The
Automaton.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [1. Environment Variables](#1-environment-variables)
  - [2. Google OAuth Credentials](#2-google-oauth-credentials)
  - [3. API Keys and User IDs](#3-api-keys-and-user-ids)
  - [4. YAML Configuration](#4-yaml-configuration)
- [Running the Workflows](#running-the-workflows)

## Prerequisites

- **Python 3.8+**: Ensure you have a recent version of Python installed.
- **Git**: Required for cloning the repository and managing versions.
- **PowerShell**: The primary interface for running workflows.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/jaipkapoor99/The-Automaton.git
    cd The-Automaton
    ```

2. **Install Python dependencies:**

    ```bash
    pip install -r scripts/requirements.txt
    ```

## Configuration

### 1. Environment Variables

Create a `.env` file in the root of the project by copying the example
file:

```bash
cp .env.example .env
```

This file will store all your sensitive data, such as API keys and user IDs.

### 2. Google OAuth Credentials

To sync with Google services, you'll need to set up OAuth 2.0 credentials.

1. **Go to the Google Cloud Console**:
    Navigate to the [APIs & Services
    dashboard](https://console.cloud.google.com/apis/dashboard).

2. **Create a new project**:
    If you don't have one already, create a new project.

3. **Enable APIs**:
    Enable the **Google Drive API** and the **Google Docs API**.

4. **Create OAuth credentials**:
   - Go to the [Credentials
       page](https://console.cloud.google.com/apis/credentials).
   - Click **Create Credentials** and select **OAuth client ID**.
   - Choose **Desktop app** as the application type.
   - Download the JSON file.

5. **Set environment variables**:
    Open your `.env` file and fill in the following variables using the
    information from your downloaded JSON file:
   - `GOOGLE_PROJECT_ID`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_AUTH_URI`
   - `GOOGLE_TOKEN_URI`
   - `GOOGLE_AUTH_PROVIDER_X509_CERT_URL`
   - `GOOGLE_REDIRECT_URIS`

### 3. API Keys and User IDs

Fill in the remaining variables in your `.env` file with your personal API
keys and user IDs for the services you want to use.

### 4. YAML Configuration

The `config.yaml` file contains the general configuration for the project.
You can customize paths, API endpoints, and other settings here. The
defaults are sensible for most users.

## Running the Workflows

All workflows are run through the `workflow.ps1` script in the `scripts`
directory.

- **To see a list of all available actions**:

    ```powershell
    .\scripts\workflow.ps1 -Action help
    ```

- **To run a specific action**:

    ```powershell
    .\scripts\workflow.ps1 -Action <action_name>
    ```
