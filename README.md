# DoveFetch a Self-Hosted Email Fetcher and IMAP Server

This project provides a containerized email solution that fetches emails from an external email provider using POP3 and serves them locally through a Dovecot IMAP server. It's designed to be used a normal email storage this meant that the email provider is used as a buffer that be permantly stored locally.

## Features

*   Fetches emails from a remote server via POP3.
*   Monitors for new emails using IMAP IDLE.
*   Stores emails in a local Maildir format.
*   Serves emails locally using a Dovecot IMAP server.
*   User and password management via an interactive shell.
*   Encrypts user passwords in the database.
*   Nginx reverse proxy for SMTP.
*   Stunnel for SSL/TLS encryption.
*   Multi-domain support.

## How it Works

The application runs in a container (e.g., Docker or Podman).

*   On the first run, it generates a new encryption key and creates a SQLite database to store user information.
*   For subsequent runs, it requires the encryption `KEY` to be provided as an environment variable to decrypt the stored credentials.
*   It starts a background process (`fetcher`) that polls a remote email server for each configured user.
*   It configures and runs a Dovecot IMAP server, allowing local email clients to connect and read the fetched emails.
*   An interactive shell is provided in the container's terminal for managing user accounts.
*   Nginx is used as a reverse proxy for SMTP, and it uses an authentication proxy to validate users.
*   Stunnel is used to provide SSL/TLS encryption for the SMTP connection.

## Getting Started

> ⚠️ It's best to use this in a container-network or in a trusted network

### Prerequisites

*   A container runtime like Docker or Podman.

### Build the Container

```sh
podman build -t dovefetch .
```

### First Run

1.  Create a directory to store mail data:
    ```sh
    mkdir mail
    ```
2.  Run the container for the first time:
    ```sh
    podman run -it -v ./mail:/mail:Z --userns=keep-id -p 1143:143 -p 1110:110 -p 25:25 --name dovefetch dovefetch
    ```
3.  On the first run, a new encryption `KEY` will be generated and printed to the console. **Save this key!** You will need it for all future runs.

    Example output:
    ```
    key: your-newly-generated-key
    Created (or verified) DB at: /mail/sqlite.db
    ...
    ```
### Subsequent Runs

To start the container again after the initial setup, you must provide the saved key as an environment variable.

```sh
podman run -it -v ./mail:/mail:Z --userns=keep-id -p 1143:143 -p 1110:110 -p 25:25 -e KEY="your-saved-key" --name dovefetch dovefetch
```

## User Management

Once the container is running, you will be dropped into an interactive shell (`MailShell`) to manage users. The `userid` and `password` should correspond to the credentials of the *external* email account you want to fetch mail from.

*   **Add a user:**
    ```
    mail> add_user <userid> <password>
    ```
*   **List users:**
    ```
    mail> list_users
    ```
*   **Delete a user:**
    ```
    mail> delete_user <userid>
    ```
*   **Exit the shell:**
    ```
    mail> exit
    ```
## Connecting an Email Client

### IMAP (Incoming Mail)

You can connect any standard email client (like Thunderbird, Outlook, or K-9 Mail) to the local Dovecot server.

*   **IMAP Server:** `localhost` (or the IP address of the machine running the container)
*   **Port:** `143`
*   **Username:** The `<userid>` you added via the shell.
*   **Password:** The `<password>` you added for that user.
*   **Security:** No SSL/TLS.

### SMTP (Outgoing Mail)

*   **SMTP Server:** `localhost` (or the IP address of the machine running the container)
*   **Port:** `25`
*   **Username:** The `<userid>` you added via the shell.
*   **Password:** The `<password>` you added for that user.
*   **Security:** No SSL/TLS.

## Planned Features
*   **Better security** as of now there is no SSL/TLS (as per the default configuration). This is not secure for production use over a network.
*   Thinking for more ^v^

## Contribution
* I will allow pr later on. but feel free to leave suggestions in the issues.
