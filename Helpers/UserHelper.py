from Helpers import OriginHelper
from Helpers import DMHelper

# Helper function to get discord user name of the poster
async def GetDisplayName(message, userid, bot):
  Origin = await OriginHelper.GetOrigin(message)
  guild = bot.get_guild(Origin)
  if not Origin:
    await DMHelper.DMUser(message, "Something went wrong retrieving the server ID")
    return

  try:
    member_obj = await guild.fetch_member(userid)
  except:
    await DMHelper.DMUser(message, "Something went wrong retrieving this users display name, perhaps they have left the server")
  try:
    if member_obj:
      display_name = member_obj.display_name
      return display_name
  except:
    await DMHelper.DMUser(message, "Something went wrong retrieving the users' display name")
    return

  if not display_name:
    await DMHelper.DMUser(message, "Something went wrong retrieving the users' display name")
    return
  return display_name

async def GetUserID(message):
  userid = message.author.id

  if not userid:
    await DMHelper.DMUser(message, "Something went wrong retrieving the user id")
    return
  return userid
