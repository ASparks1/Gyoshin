import discord
import datetime
date = datetime.date.today()
from datetime import datetime
from Helpers import DMHelper

async def ValidateDateTime(ctx, day, month, year, hour, minute):
  UserID = ctx.author.id
  current_date = discord.utils.utcnow().strftime("%Y-%m-%d %H:%M")
  newdatetime = f"{year}-{month}-{day} {hour}:{minute}"

  try:
    newdatetime = datetime.strptime(newdatetime, "%Y-%m-%d %H:%M")
  except:
    await DMHelper.DMUserByID(bot, UserID, "Unable to parse given date")

  try:
    newdatetime = datetime.strftime(newdatetime, "%Y-%m-%d %H:%M")
  except:
    await DMHelper.DMUserByID(bot, UserID, "Unable to format given date")

  validdate = (bool(newdatetime >= current_date))
  return validdate
