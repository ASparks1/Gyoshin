from Helpers import OriginHelper
from Helpers import DMHelper

# Helper function to get discord user name of the poster
async def GetDisplayName(ctx, userid, bot):
  Origin = await OriginHelper.GetOrigin(ctx, bot, userid)
  guild = bot.get_guild(Origin)
  if not Origin:
    await DMHelper.DMUserByID(bot, userid, "Something went wrong retrieving the server ID")
    return

  try:
    member_obj = await guild.fetch_member(userid)
  except:
    await DMHelper.DMUserByID(bot, userid, "Something went wrong retrieving this users display name, perhaps they have left the server")
  try:
    if member_obj:
      display_name = member_obj.display_name
      return display_name
  except:
    await DMHelper.DMUserByID(bot, userid, "Something went wrong retrieving the users' display name")
    return

  if not display_name:
    await DMHelper.DMUserByID(bot, userid, "Something went wrong retrieving the users' display name")
    return
  return display_name

async def GetUserID(ctx, userid, bot):
  userid = ctx.author.id

  if not userid:
    await DMHelper.DMUserByID(bot, userid, "Something went wrong retrieving the user id")
    return
  return userid
