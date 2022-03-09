import sqlite3
import asyncio
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import DMHelper
from discord import ChannelType

async def DeleteTemplate(ctx, bot):
  try:
    UserID = ctx.author.id
    Origin = await OriginHelper.GetOrigin(ctx, bot, UserID)
    GuildName = await OriginHelper.GetName(ctx, bot, UserID)
  except:
     await DMHelper.DMUserByID(bot, UserID, "Something went wrong when gathering server and user information.")
     return

  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == ctx.author

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute("SELECT Name FROM Templates WHERE CreatorUserID = (?) AND Origin = (?)", (UserID, Origin,))
  rows = c.fetchall()

  if not rows:
    await DMHelper.DMUserByID(bot, UserID, f"You have not created any templates on the {GuildName} server")
    conn.close()
    return

  if rows:
    Message = None
    for row in rows:
      Name = row[0]
      if not Message:
        Message = f"{Name}"
      elif Message:
        Message = f"{Message}, {Name}"

    await DMHelper.DMUserByID(bot, UserID, f"You have created the following templates on the {GuildName} server:\n{Message}")
    ValidTemplateName = None
    while not ValidTemplateName:
      await DMHelper.DMUserByID(bot, UserID, "Please provide the name of the template you wish to delete")
      try:
        response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
        TemplateName = response.content
        c.execute("SELECT ID FROM Templates WHERE Name = (?) AND Origin = (?)", (TemplateName, Origin,))
        row = c.fetchone()
        if not row:
          await DMHelper.DMUserByID(bot, UserID, "Please enter a valid template name.")
          continue
        if row:
          ValidTemplateName = 'yes'
          try:
            CanDelete = None
            while not CanDelete:
              await DMHelper.DMUserByID(bot, UserID, f"Do you want to delete the template {TemplateName} on the {GuildName} server? (Y/N)")
              response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
              if response.content in("Y","y","Yes","yes"):
                CanDelete = 'yes'
                c.execute("DELETE FROM Templates WHERE Name = (?) AND Origin = (?)", (TemplateName, Origin,))
                conn.commit()
                conn.close()
                await DMHelper.DMUserByID(bot, UserID, "Template succesfully deleted.")
              elif response.content in("N","n","No","no"):
                CanDelete = "no"
                conn.close()
                return
              else:
               await DMHelper.DMUserByID(bot, UserID, "Invalid answer detected, please respond with yes or no.")
               continue
          except asyncio.TimeoutError:
            await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a template.")
            conn.close()
            return
      except asyncio.TimeoutError:
        await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a template.")
        conn.close()
        return
