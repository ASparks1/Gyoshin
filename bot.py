import os
from datetime import datetime
import discord
import dotenv
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord import app_commands
from discord_components import DiscordComponents, Button, ButtonStyle
from Commands import Templates
from Commands import AddDefaultTemplates
from Commands import AddTemplate
from Commands import DeleteTemplate
from Commands import Runs
from Commands import Commands
from Commands import Dismiss
from Commands import AddRun
from Commands import MyRuns
from Helpers import DeleteOldRaidDataHelper
from Helpers import ButtonInteractionHelper
from Helpers import MemberHelper

# Enable privileged gateway intents as described on
# https://discordpy.readthedocs.io/en/latest/intents.html
# so we can access member objects to retrieve display names and use reactions
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.message_content = True

bot = commands.Bot(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
  guilds = len(bot.guilds)
  print(f"Ready, I'm active in {guilds} servers!")
  DiscordComponents(bot)

  # Nightly job to clean up old data
  @tasks.loop(minutes=60.0)
  async def CleanUpOldRaidData():
    if datetime.utcnow().hour == 5:
      print("Starting cleanup of old raid data!")
      await DeleteOldRaidDataHelper.DeleteOldRaidData()
  CleanUpOldRaidData.start()

# Clean up a users' data after they've been kicked or have left the server
@bot.event
async def on_member_remove(member):
  print("a member has left the server, starting cleanup of their data!")
  await MemberHelper.OnMemberLeaveOrRemove(member)

# Bot commands
@tree.command()
async def templates(interaction: discord.Interaction, ctx):
  await Templates.GetTemplates(ctx.message)

@tree.command()
async def runs(interaction: discord.Interaction, ctx, bot):
  await Runs.ListRunsOnDate(ctx.message, bot)  

@tree.command()
async def commands(interaction: discord.Interaction, ctx, bot):
  await Runs.ListRunsOnDate(ctx.message, bot)  

@tree.command()
async def addrun(interaction: discord.Interaction, ctx, bot):
  await AddRun.AddRunInDM(ctx.message, bot)
  
@tree.command()
async def adddefaulttemplates(interaction: discord.Interaction, ctx):
 await AddDefaultTemplates.AddDefaultTemplates(ctx.message)

@tree.command()
async def addtemplate(interaction: discord.Interaction, ctx, bot):
 await AddTemplate.AddTemplate(ctx.message, bot)

@tree.command()
async def deletetemplate(interaction: discord.Interaction, ctx, bot):
 await DeleteTemplate.DeleteTemplate(ctx.message, bot)

@tree.command()
async def dismiss(interaction: discord.Interaction, ctx, bot):
 await DeleteTemplate.DeleteTemplate(ctx.message, bot)

@tree.command()
async def myruns(interaction: discord.Interaction, ctx, bot):
 await MyRuns.ListMyRuns(ctx.message, bot)

# Message events
# Do nothing if the message is from the bot
@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  # Process commmands if found in message
  await bot.process_commands(message)

# Button events
@bot.event
async def on_button_click(interaction):
  await ButtonInteractionHelper.OnButtonClick(interaction, bot)

# Get bot token and run on server
load_dotenv()
bot.run(os.getenv('Token'))
