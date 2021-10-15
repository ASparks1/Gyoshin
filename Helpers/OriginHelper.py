from Helpers import DMHelper

#Helper function to retrieve discord server ID
async def GetOrigin(message):
    try:
      origin = message.guild.id
      return origin
    except:
      await DMHelper.DMUser(message, "Something went wrong resolving the server ID, please make sure you're calling the command from a channel in the server and not in a DM")

async def GetName(message):
  try:
    GuildName = message.guild.name
    return GuildName
  except:
    await DMHelper.DMUser(message, "Something went wrong resolving the server name, please make sure you're calling the command from a channel in the server and not in a DM")
