import discord
from discord import app_commands
from discord.ext import commands
from database import set_trap_channel

class TrapChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, admin_role_id: int):
        super().__init__(
            placeholder="Выберите текстовый канал...",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1
        )
        self.admin_role_id = admin_role_id

    async def callback(self, interaction: discord.Interaction):
        # Double check role permissions
        if not any(role.id == self.admin_role_id for role in interaction.user.roles):
            return

        channel_select = self.values[0]
        guild = interaction.guild

        if not guild:
            return

        # Retrieve the full TextChannel object from cache or API
        channel = guild.get_channel(channel_select.id)
        if not channel:
            try:
                channel = await guild.fetch_channel(channel_select.id)
            except discord.HTTPException:
                pass

        if not channel or not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                content="❌ Ошибка: не удалось найти выбранный текстовый канал.",
                ephemeral=True
            )
            return

        # Save the trap channel to the database
        set_trap_channel(guild.id, channel.id)

        # Defer interaction since purging and sending embeds can take time
        await interaction.response.defer(ephemeral=True)

        try:
            # Clear all messages in the channel
            await channel.purge(limit=None)

            # Create a warning embed matching the user's reference image in Russian
            embed = discord.Embed(
                title="🚫 Не пишите сюда",
                description=(
                    "**Этот канал не предназначен для общения.**\n\n"
                    "Если вы отправите сообщение сюда, вы будете:\n"
                    "• **Отправлены в таймаут на 1 час**\n"
                    "• **Все ваши сообщения за последний час будут удалены**\n\n"
                    "KavkazTuning Security"
                ),
                color=0xE02828  # Vibrant red matching the reference image border
            )

            # Send the warning embed to the channel
            await channel.send(embed=embed)

            # Acknowledge to the administrator
            await interaction.followup.send(
                content=f"✅ Канал {channel.mention} успешно очищен и настроен как запрещенная зона.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                content=f"❌ Произошла ошибка при очистке/настройке канала: {e}",
                ephemeral=True
            )

class SetupTrapView(discord.ui.View):
    def __init__(self, admin_role_id: int):
        super().__init__(timeout=180)
        self.add_item(TrapChannelSelect(admin_role_id))

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setup_trap", description="Настроить канал запрещенной зоны (Только для Администрации)")
    async def setup_trap(self, interaction: discord.Interaction):
        # Ignore if command is called in a direct message
        if not interaction.guild:
            return

        # Check if the command is running in the configured guild
        if interaction.guild_id != self.bot.target_guild_id:
            return

        # Check if user has the admin role configured in config.json
        if not any(role.id == self.bot.admin_role_id for role in interaction.user.roles):
            # Otherwise - nothing happens
            return

        view = SetupTrapView(self.bot.admin_role_id)
        await interaction.response.send_message(
            content="Выберите текстовый канал из списка, который будет использоваться как запрещенная зона:",
            view=view,
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
