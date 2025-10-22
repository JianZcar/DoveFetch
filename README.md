# DoveFetch a Self-Hosted Email Fetcher and IMAP/SMTP Server

This project provides a containerized email solution that fetches emails from an external email provider using POP3 and serves them locally through a Dovecot IMAP server. It’s designed to function as a full IMAP/SMTP server and local mail storage solution. The external email provider acts only as a temporary relay, while all emails are permanently stored and managed locally.

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
*   Webmail access via Roundcube.

## Supported Email providers.
*   Disroot
*   Help me add your email provider by posting an issue or by giving a pr (oauth2 is not supported currently)

## How it Works

The application runs in a container (e.g., Docker or Podman).

*   On the first run, it generates a new encryption key and creates a SQLite database to store user information.
*   For subsequent runs, it requires the encryption `KEY` to be provided as an environment variable to decrypt the stored credentials.
*   Starts a background process (fetcher) that monitors remote email servers for each configured user. It primarily uses IMAP to detect mailbox changes in real time, with periodic polling as a fallback to ensure no messages are missed.
*   It configures and runs a Dovecot IMAP server, allowing local email clients to connect and read the fetched emails.
*   An interactive shell is provided in the container's terminal for managing user accounts.
*   Nginx is used as a reverse proxy for SMTP, and it uses an authentication proxy to validate users.
*   Stunnel is used to provide SSL/TLS encryption for the SMTP connection.

## Getting Started

> ⚠️ It's best to use this in a container-network or in a trusted network

### Prerequisites

*   A container runtime like Docker or Podman.

### First Run

1. Clone the repository and change directory:

   ```sh
   git clone git@github.com:JianZcar/DoveFetch.git
   cd DoveFetch
   ```

2. Build the main container:
    ```sh
    podman build -t dovefetch .
    ```

3.  Create a directory to store mail data:
    ```sh
    mkdir mail
    ```
4.  Run the container for the first time:
    ```sh
    podman run -it -v ./mail:/mail:Z -p 143:143 -p 993:993 -p 25:25 -p 465:465 --name dovefetch dovefetch
    ```
5.  On the first run, a new encryption `KEY` will be generated and printed to the console. **Save this key!** You will need it for all future runs.

    Example output:
    ```
    key: your-newly-generated-key
    Created (or verified) DB at: /mail/sqlite.db
    ...
    ```
### Subsequent Runs

To start the container again after the initial setup, you must provide the saved key as an environment variable.

```sh
podman run -it -v ./mail:/mail:Z -p 143:143 -p 993:993 -p 25:25 -p 465:465 -e KEY="your-saved-key" --name dovefetch dovefetch
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

## Webmail (Roundcube)

This project includes a separate Docker container for Roundcube webmail.

### Building and Running Roundcube

1.  Build the Roundcube container:
    ```sh
    podman build -t roundcube -f roundcube/Containerfile .
    ```
2.  Run the Roundcube container:
    ```sh
    podman run -d -p 8080:80 --name roundcube roundcube
    ```
    This will start Roundcube on `http://localhost:8080`.


### Running both DoveFetch and Roundcube

1.  Create a network
    ```sh
    podman network create mailnet
    ```

2.  Run DoveFetch (setting the ip 10.89.0.10 is required for secure connection to work between to container)
    ```sh
    podman run -dit --name dovefetch \
                   --network mailnet --ip 10.89.0.10 \
                   -v /path/to/Maildir:/mail:Z \
                   -e KEY=YOUR_KEY \
                   dovefetch
    ```

3.  Run Roundcube
    ```sh

    podman run -d --name roundcube \
               --network mailnet \
               -p 8080:80 \
               -e ROUNDCUBEMAIL_DEFAULT_HOST=ssl://10.89.0.10 \
               -e ROUNDCUBEMAIL_DEFAULT_PORT=993 \
               -e ROUNDCUBEMAIL_SMTP_SERVER=ssl://10.89.0.10 \
               -e ROUNDCUBEMAIL_SMTP_PORT=465 \
               roundcube


    ```

### Configuring Roundcube

1.  Access Roundcube at `http://localhost:8080`.
2.  On the login page, click on the gear icon to open the server settings.
3.  Configure the IMAP and SMTP server settings as follows:
    *   **IMAP Server:** `host.containers.internal` (or the IP address of the machine running the `dovefetch` container)
    *   **IMAP Port:** `143`
    *   **SMTP Server:** `host.containers.internal` (or the IP address of the machine running the `dovefetch` container)
    *   **SMTP Port:** `25`
    *   **Username:** The `<userid>` you added via the shell.
    *   **Password:** The `<password>` you added for that user.

## Connecting an Email Client

### IMAP (Incoming Mail)

You can connect any standard email client (like Thunderbird, Outlook, or K-9 Mail) to the local Dovecot server.

*   **IMAP Server:** `localhost` (or the IP address of the machine running the container)
*   **Port:** `143` (No SSL/TLS) or `993` (SSL/TLS)
*   **Username:** The `<userid>` you added via the shell.
*   **Password:** The `<password>` you added for that user.

### SMTP (Outgoing Mail)

*   **SMTP Server:** `localhost` (or the IP address of the machine running the container)
*   **Port:** `25` (No SSL/TLS) or `465` (SSL/TLS)
*   **Username:** The `<userid>` you added via the shell.
*   **Password:** The `<password>` you added for that user.

## Planned Features
*   Oauth2
*   Thinking for more ^v^

## Contribution
* Feel free to leave an issue or pr

> ⚠️ Use at your own risk, I'm not liable for any data loss.
