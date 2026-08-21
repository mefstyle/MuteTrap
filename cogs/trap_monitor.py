import datetime
import logging
import asyncio
import discord
from discord.ext import commands
from database import get_trap_channel

logger = logging.getLogger("TrapMonitor")

class TrapMonitorCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore direct messages (DMs)
        if not message.guild:
            return

        # Ignore messages that are not from our target guild
        if message.guild.id != self.bot.target_guild_id:
            return

        # Ignore bot messages to prevent loop triggers
        if message.author.bot:
            return

        # Retrieve the trap channel ID for this guild
        trap_channel_id = get_trap_channel(message.guild.id)
        if not trap_channel_id or message.channel.id != trap_channel_id:
            return

        member = message.author
        if not isinstance(member, discord.Member):
            return

        # Check if the sender is an administrator or has the admin role from config.json
        is_admin = member.guild_permissions.administrator or any(
            role.id == self.bot.admin_role_id for role in member.roles
        )
        if is_admin:
            logger.info(f"Admin/Moderator {member} sent a message in the trap channel. Ignored.")
            return

        logger.info(f"User {member} (ID: {member.id}) sent a message in the trap channel. Executing punishment...")

        # 1. Immediate Timeout
        timeout_duration = datetime.timedelta(hours=1)
        try:
            await member.timeout(
                timeout_duration,
                reason="Отправка сообщения в запрещенный канал (автомодерация)"
            )
            logger.info(f"Timed out user {member} for 1 hour.")
        except discord.Forbidden:
            logger.error(f"Cannot timeout {member}. Insufficient permissions (bot role might be lower).")
        except discord.HTTPException as e:
            logger.error(f"HTTP error timing out {member}: {e}")

        # 2. Immediate deletion of the triggering message to hide it instantly
        try:
            await message.delete()
        except discord.HTTPException as e:
            logger.warning(f"Could not delete triggering message from {member}: {e}")

        # 3. Clean up all messages from this user in the last hour across the entire server in the background
        async def purge_user_history():
            one_hour_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
            deleted_count = 0
            
            for channel in message.guild.text_channels:
                # Verify bot permissions in the channel
                perms = channel.permissions_for(message.guild.me)
                if not (perms.read_messages and perms.read_message_history and perms.manage_messages):
                    continue

                try:
                    # Fetch and delete messages from this user
                    async for msg in channel.history(after=one_hour_ago, limit=None):
                        if msg.author.id == member.id:
                            try:
                                await msg.delete()
                                deleted_count += 1
                            except discord.HTTPException:
                                pass
                except discord.Forbidden:
                    pass
                except Exception as e:
                    logger.error(f"Error purging messages in channel {channel.name}: {e}")

            logger.info(f"Successfully purged {deleted_count} messages for user {member} across the server.")

        # Run the purging process asynchronously to ensure bot response is instant
        asyncio.create_task(purge_user_history())

async def setup(bot: commands.Bot):
    await bot.add_cog(TrapMonitorCog(bot))
