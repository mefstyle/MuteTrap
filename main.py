import os
import json
import logging
import discord
from discord.ext import commands
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("BotMain")

CONFIG_PATH = "config.json"

if not os.path.exists(CONFIG_PATH):
    logger.error(f"Configuration file {CONFIG_PATH} not found!")
    exit(1)

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception as e:
    logger.error(f"Failed to read or parse {CONFIG_PATH}: {e}")
    exit(1)

BOT_TOKEN = config.get("bot_token")
GUILD_ID = config.get("guild_id")
ADMIN_ROLE_ID = config.get("admin_role_id")

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    logger.error("Please set a valid bot_token in config.json")
    exit(1)

try:
    GUILD_ID = int(GUILD_ID)
    ADMIN_ROLE_ID = int(ADMIN_ROLE_ID)
except (ValueError, TypeError):
    logger.error("guild_id and admin_role_id in config.json must be valid integers.")
    exit(1)

# Initialize SQLite database
init_db()

# Gateway Intents
intents = discord.Intents.default()
intents.message_content = True  # Crucial to inspect messages in the trap channel
intents.members = True          # Crucial to fetch and moderate members
intents.guilds = True           # Crucial to fetch guild and channels

class KavkazTuningBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.target_guild_id = GUILD_ID
        self.admin_role_id = ADMIN_ROLE_ID

    async def setup_hook(self):
        # Load extensions/cogs
        await self.load_extension("cogs.admin")
        await self.load_extension("cogs.trap_monitor")
        logger.info("Loaded cogs: cogs.admin, cogs.trap_monitor")

        # Sync commands only to the configured guild
        guild_object = discord.Object(id=self.target_guild_id)
        self.tree.copy_global_to(guild=guild_object)
        await self.tree.sync(guild=guild_object)
        logger.info(f"Slash commands synchronized with guild {self.target_guild_id}")

    async def on_ready(self):
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Target Guild: {self.target_guild_id}")
        logger.info(f"Admin Role ID: {self.admin_role_id}")

bot = KavkazTuningBot()

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
