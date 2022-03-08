import os
from datetime import datetime
import discord
import dotenv
from dotenv import load_dotenv
from discord.ext import commands, tasks
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

@bot.event
async def on_ready():
  guilds = len(bot.guilds)
  print(f"Ready, I'm active in {guilds} servers!")
  DiscordComponents(bot)

  # Nightly job to clean up old data
  @tasks.loop(minutes=60.0)
  async def CleanUpOldRaidData():
    if discord.utils.utcnow().hour == 5:
      print("Starting cleanup of old raid data!")
      await DeleteOldRaidDataHelper.DeleteOldRaidData()
  CleanUpOldRaidData.start()

# Clean up a users' data after they've been kicked or have left the server
@bot.event
async def on_member_remove(member):
  print("a member has left the server, starting cleanup of their data!")
  await MemberHelper.OnMemberLeaveOrRemove(member)

# Bot commands
@bot.slash_command()
async def templates(ctx):
 """Lists all available templates on the server"""
 await ctx.defer(hidden=True)
 await Templates.GetTemplates(ctx.message)

@bot.slash_command()
async def runs(ctx):
 """Lists all runs on a given date"""
 await ctx.defer(hidden=True)
 await Runs.ListRunsOnDate(ctx.message, bot)  

@bot.slash_command()
async def addrun(ctx):
 """Starts a conversation where the bot guides you through the process to create a run"""
 await ctx.defer(hidden=True)
 await AddRun.AddRunInDM(ctx.message, bot)
  
@bot.slash_command()
async def adddefaulttemplates(ctx):
 """Adds some default templates for FFXIV to the server"""
 await ctx.defer(hidden=True)
 await AddDefaultTemplates.AddDefaultTemplates(ctx.message)

@bot.slash_command()
async def addtemplate(ctx):
 """Starts a conversation where the bot guides you through the process to add a template"""
 await ctx.defer(hidden=True)
 await AddTemplate.AddTemplate(ctx.message, bot)

@bot.slash_command()
async def deletetemplate(ctx):
 """Gives the creator of a template the option to delete it"""
 await ctx.defer(hidden=True)
 await DeleteTemplate.DeleteTemplate(ctx.message)

@bot.slash_command()
async def myruns(ctx):
 """Lists upcoming runs you've signed up for up to a maxium of 5"""
 await ctx.defer(hidden=True)
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
