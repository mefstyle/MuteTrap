# 🚫 MuteTrap — Discord Auto-Moderation Honeypot Bot

**MuteTrap** is a specialized Discord security bot designed to protect servers from compromised user accounts and automated spam bots distributing malicious links (such as "free money" scams impersonating MrBeast, Mellstroy casino promotions, crypto scams, and other malware).

---

## 💡 How It Works (The Honeypot Concept)

Spam bots typically use automated scripts to join servers and aggressively post spam links across **every single text channel** they can access. MuteTrap exploits this behavior using a simple honeypot mechanism:

1. You create a dedicated trap channel on your server (e.g., `#🚫-do-not-write-here`).
2. Regular users see the warning banner inside the channel and ignore it.
3. A spam bot joins the server, ignores the rules, and attempts to post its spam in the trap channel.
4. **The bot reacts immediately:**
   * Places the spammer in a **1-hour timeout (mute)**.
   * **Deletes the triggering message** from the trap channel instantly.
   * Starts a background task to scan all other channels on the server and **purges all messages** sent by this user in the last hour.
5. The spam is eliminated guild-wide within seconds, and the compromised account is muted.

---

## 🛠️ Features

* ⚡ **Instant Punishment**: Timeout is applied immediately upon sending a message to the trap channel.
* 🧹 **Guild-Wide Cleanup**: Automatically scans and deletes all other messages from the spammer across the entire server sent in the last hour (processed asynchronously in the background).
* 🛡️ **Admin & Moderator Immunity**: Server administrators and users with the configured moderator role are immune to the trap to prevent accidental mute of staff.
* 🤖 **Easy Setup**: Initialize the trap channel using the `/setup_trap` slash command. The bot will automatically purge the channel and post a warning banner (Embed).
* 🗄️ **Lightweight Database**: Uses SQLite to keep track of configured trap channels without requiring external database setups.

---

## 📦 Requirements

* **Python** 3.8 or higher.
* Dependencies: `discord.py` version 2.3.0 or higher (see requirements.txt).
* A Discord Bot Token with **Privileged Gateway Intents** enabled.

---

## 🚀 Installation & Setup

### Step 1: Create a Bot on the Discord Developer Portal
1. Navigate to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a **New Application**, go to the **Bot** tab, and generate a token.
3. Save the **Token**—you will need to add it to your configuration.
4. In the **Bot** section, scroll down to **Privileged Gateway Intents** and enable:
   * **Presence Intent**
   * **Server Members Intent** (required to manage members and apply timeouts)
   * **Message Content Intent** (required to read messages in the trap channel)
5. Go to **OAuth2** -> **URL Generator**:
   * Under **Scopes**, select `bot` and `applications.commands`.
   * Under **Bot Permissions**, select `Administrator` (or grant specific permissions: Manage Messages, Read Message History, Moderate Members, Send Messages, Read Messages).
   * Copy the generated link and invite the bot to your server.

### Step 2: Install Dependencies
Clone/download the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### Step 3: Configure the Bot
Open config.json and replace the placeholder values with your credentials:

```json
{
  "bot_token": "YOUR_BOT_TOKEN_HERE",
  "guild_id": 123456789012345678,
  "admin_role_id": 123456789012345678
}
```

* `bot_token`: Your Discord bot token.
* `guild_id`: The ID of your Discord server (guild) where the bot will operate.
* `admin_role_id`: The ID of the administrator/moderator role. Users with this role will be able to run configuration commands and will not be muted if they post in the trap channel.

> 💡 **Tip:** To get these IDs, enable **Developer Mode** in Discord (User Settings -> Advanced -> Developer Mode). Then right-click a server or role and click **Copy ID**.

### Step 4: Run the Bot
Run the bot script:
```bash
python main.py
```

---

## ⚙️ In-Server Setup

1. Create a new text channel on your server (e.g., `#🚫-spam-trap`).
2. Make sure the bot has permissions to View Channel, Send Messages, Read Message History, and Manage Messages in that channel.
3. Use the `/setup_trap` slash command on your server.
4. Select the created channel from the dropdown menu.
5. The bot will automatically:
   * Purge any existing messages in the channel.
   * Send a warning banner (Embed) explaining that users should not write there.
   * Register the channel in the database as the active honeypot.

**All set!** Any spam bot that attempts to scan and write into this channel will be immediately timed out and cleaned up.
