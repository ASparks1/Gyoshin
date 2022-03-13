import discord
from discord.ext import commands
from Helpers import ButtonInteractionHelper

class RaidInfoView(discord.ui.View):
  def __init__(self, bot, ctx, *args, **kwargs):
    if bot is not None:
      self.bot=bot
    if ctx is not None:
      self.ctx=ctx
    super(RaidInfoView, self).__init__(timeout=None, *args, **kwargs)

  @discord.ui.button(label="Tank", row=0, style=discord.ButtonStyle.primary, custom_id="tank_btn")
  async def tank(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)

  @discord.ui.button(label="Dps", row=0, style=discord.ButtonStyle.danger, custom_id="dps_btn")
  async def dps(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)

  @discord.ui.button(label="Healer", style=discord.ButtonStyle.success, custom_id="healer_btn")
  async def healer(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)

  @discord.ui.button(label="Rally", custom_id="rally_btn")
  async def rally(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)

  @discord.ui.button(label="Members", row=1, custom_id="members_btn")
  async def members(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)

  @discord.ui.button(label="Reserves", row=1, custom_id="reserves_btn")
  async def reserves(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)

  @discord.ui.button(label="Message members", row=1, custom_id="messageraidmembers_btn")
  async def messagemembers(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)

  @discord.ui.button(label="Dismiss members", row=1, custom_id="dismissmembers_btn")
  async def dismissmembers(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)

  @discord.ui.button(label="Edit description", row=2, custom_id="editdesc_btn")
  async def editdesc(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)

  @discord.ui.button(label="New organizer", row=2, custom_id="neworganizer_btn")
  async def neworganizer(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)

  @discord.ui.button(label="Reschedule", row=2, custom_id="reschedule_btn")
  async def reschedule(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)

  @discord.ui.button(label="Cancel", row=2, style=discord.ButtonStyle.danger, custom_id="cancel_btn")
  async def cancel(self, interaction: discord.Interaction, bot, ctx):
    await interaction.response.send_message(content="Processing", ephemeral=True)
    await ButtonInteractionHelper.OnButtonClick(interaction, bot, ctx)
