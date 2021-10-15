from Helpers import DMHelper

#Helper function to retrieve discord server ID
async def GetOrigin(message):
  if not message:
    # Throw error when no message input is received
    await DMHelper.DMUser(message, "No message received")
    return
  else:
    try:
      origin = message.guild.id  
      return origin
    except:
      await DMHelper.DMUser(message, "Something went wrong resolving the server ID, please make sure you're calling the command from a channel in the server and not in a DM")
    
async def GetName(message):
  if not message:
    # Throw error when no message input is received
    await DMHelper.DMUser(message, "No message received")
    return
  else:
    GuildName = message.guild.name  
    return GuildName