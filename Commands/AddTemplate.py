import sqlite3
import asyncio
from Helpers import AddTemplateHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import DMHelper
from discord import ChannelType

async def AddTemplate(ctx, bot):
  #try:
  UserID = ctx.author.id
  Origin = await OriginHelper.GetOrigin(ctx, bot, UserID)
  GuildName = await OriginHelper.GetName(ctx, bot, UserID)
  Creator = await UserHelper.GetUserID(ctx, UserID, bot)
  CreatorDisplay = await UserHelper.GetDisplayName(ctx, Creator, bot)
  #except:
  #   await DMHelper.DMUserByID(bot, UserID, "Something went wrong when gathering server and user information.")
  #   return

  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == ctx.author

  await DMHelper.DMUserByID(bot, UserID, f"Hi {CreatorDisplay}, let's create a template in the {GuildName} server.\nFirst, give me the name of your template, please beware that spaces are not allowed in template names.\n")
  try:
    response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
  except asyncio.TimeoutError:
    await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a template.")
    return

  TemplateName = response.content
  if TemplateName:
    try:
      conn = sqlite3.connect('RaidPlanner.db')
      c = conn.cursor()
      c.execute("SELECT ID FROM Templates WHERE Name = (?) AND Origin = (?)", (TemplateName, Origin,))
      row = c.fetchone()

      if row:
        await DMHelper.DMUserByID(bot, UserID, f"There already exists a template with the name {TemplateName} on the {GuildName} server")
        conn.close()
        return
      if not row:
        conn.close()
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong checking if a template with the same name already exists on this server")
      conn.close()
      return

  await AddTemplateHelper.NrOfPlayersAndConfirmSection(bot, ctx, Origin, UserID, TemplateName)
  conn.close()
  return
