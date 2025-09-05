# The Automaton Setup Guide

This guide provides detailed instructions for setting up and configuring The
Automaton.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [1. Environment Variables](#1-environment-variables)
  - [2. Google OAuth Credentials](#2-google-oauth-credentials)
  - [3. Authorizing the Application](#3-authorizing-the-application)
  - [4. API Keys and User IDs](#4-api-keys-and-user-ids)
  - [5. YAML Configuration](#5-yaml-configuration)
- [Running the Workflows](#running-the-workflows)

## Prerequisites

- **Python 3.8+**: Ensure you have a recent version of Python installed.
- **Git**: Required for cloning the repository and managing versions.
- **Bash**: The primary interface for running workflows.

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

### 3. Authorizing the Application

The first time you run a workflow that requires Google authentication (such as
`sync-gdrive`), the application will perform the following steps:

1. It will generate a unique authentication URL and save it to
    `Temp/auth_url.txt`.
2. You will be prompted to open this URL in your browser.
3. After you log in and grant permission, Google will display an
    authorization code.
4. Copy this code.
5. Create a new file named `Temp/auth_code.txt`.
6. Paste the code into this file and save it.

Once the `auth_code.txt` file is in place, you can run the workflow again.
The application will use the code to generate a `token.json` file, which
will be used for all subsequent authentications. You will not need to repeat
this process unless you revoke the application's access or delete the
`token.json` file.

### 4. API Keys and User IDs

Fill in the remaining variables in your `.env` file with your personal API
keys and user IDs for the services you want to use.

### 5. YAML Configuration

The `config.yaml` file contains the general configuration for the project.
You can customize paths, API endpoints, and other settings here. The
defaults are sensible for most users.

## Running the Workflows

All workflows are run through the `workflow.sh` script in the `scripts`
directory.

- **To see a list of all available actions**:

    ```bash
    ./scripts/workflow.sh -Action help
    ```

- **To run a specific action**:

    ```bash
    ./scripts/workflow.sh -Action <action_name>
    ```
