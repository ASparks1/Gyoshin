from Helpers import DMHelper

# Helper function to retrieve discord server ID
async def GetOrigin(ctx, bot, UserID):
    try:
      origin = ctx.guild.id
      return origin
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong resolving the server ID, please make sure you're calling the command from a channel in the server and not in a DM")

# Helper function to retrieve the server name
async def GetName(ctx, bot, UserID):
  try:
    GuildName = ctx.guild.name
    return GuildName
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong resolving the server name, please make sure you're calling the command from a channel in the server and not in a DM")