# Pterodactyl Discord Admin Bot

A production-ready Discord bot for Pterodactyl **Application API** administration. It provides slash commands for admins, operators, and viewers with RBAC, audit logging, and interactive components.

## Features
- Slash commands grouped by resource (`/servers`, `/users`, `/nodes`, `/locations`, `/nests`, `/eggs`, `/allocations`, `/dbhosts`, `/serverdb`, `/ptero`).
- RBAC with roles: **Ptero SuperAdmin**, **Ptero Operator**, **Ptero Viewer**. Per-command overrides stored in SQLite.
- Audit log channel for every write/delete action.
- Pagination, confirmation dialogs, modals for create flows, and rich embeds.
- Resilient Pterodactyl Application API client with retry for safe requests and rate-limit backoff.

## Setup
1. Python 3.10+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure credentials in `src/config.py` (placeholders are provided) or set environment variables with the same names. No `.env` file is required:
   ```python
   # src/config.py
   DISCORD_TOKEN = "your_discord_bot_token"
   DISCORD_CLIENT_ID = "your_discord_client_id"
   DISCORD_GUILD_ID = ""  # optional
   USE_PRIVILEGED_INTENTS = False  # set True only if enabled in the Discord Developer Portal
   PTERO_BASE_URL = "https://panel.example.com"
   PTERO_APPLICATION_API_KEY = "your_application_api_key"
   PTERO_BOT_DB = "bot.db"  # optional sqlite path
   ADDITIONAL_ALLOWED_ROLE_IDS = []  # e.g., [123456789012345678] for role-ID-based access
   ```
   If you enable `USE_PRIVILEGED_INTENTS`, make sure **Server Members Intent** (and Presences if needed) is toggled on in the
   Discord Developer Portal for your application; otherwise leave it `False` to avoid login failures.
4. Verify configuration loads correctly:
   ```bash
   python test_config.py
   ```
5. Run the bot (installs dependencies automatically if missing):
   ```bash
   python bot.py
   ```
   When deploying on Pterodactyl, set `BOT_PY_FILE=bot.py` and `REQUIREMENTS_FILE=requirements.txt` so the panel installs
   dependencies before launch.

6. If the bot exits with `LoginFailure: Improper token has been passed`, double-check the `DISCORD_TOKEN` value in `src/config.py`
   (or your environment) and ensure you copied the **Bot** token from the Discord Developer Portal without surrounding quotes
   or extra whitespace.

### Docker
```
docker build -t ptero-bot .
docker run --env-file .env -v $(pwd)/bot.db:/app/bot.db ptero-bot
```

## Command catalogue
- `/help` or `/ptero help` – role-aware catalogue with per-command overrides shown
- `/ptero ping` – health check
- `/ptero whoami` – API scope info
- `/ptero config` – set audit channel & default ephemerality
- `/servers list|info|create|update|suspend|unsuspend|reinstall|delete|set-owner|allocations|databases`
- `/users list|info|create|update|delete`
- `/nodes list|info|create|update|delete|allocations`
- `/locations list|create|update|delete`
- `/nests list|info` and `/eggs list|info`
- `/allocations search|create|delete`
- `/dbhosts list|create|update|delete`
- `/serverdb list|search|delete`

Write/delete operations require Operator/SuperAdmin roles; delete-only operations require SuperAdmin.

## RBAC and overrides
Roles are checked per command. To override roles for a command, insert rows into the SQLite `command_overrides` table (`command` column matches the slash command path, e.g., `servers.delete`).
If your org uses role IDs instead of the default names, populate `ADDITIONAL_ALLOWED_ROLE_IDS` in `src/config.py` (or the environment variable of the same name with a comma-separated list) to grant access without renaming roles.

## Audit logging
Set the channel once:
```
/ptero config audit_channel:#ops-audit
```
Every write/delete action posts an embed with actor, action, and target IDs.

## Slash command registration
The bot automatically syncs commands. Provide `DISCORD_GUILD_ID` during development for rapid iteration; omit it in production for global sync.

## Notes
- Sensitive tokens are never logged.
- Error handling surfaces API failures and permission errors with ephemeral replies.
