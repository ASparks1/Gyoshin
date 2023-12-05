import discord
from Helpers import DMHelper
from Helpers import OriginHelper

# Helper function to tag a list of users
async def NotifyRaidMembers(ctx, raidmembers):
  try:
    Message = None
    for member in raidmembers:
      Notification = f"<@!{member[0]}> "
      if not Message:
        Message = f"{Notification}"
      elif Message:
        Message = f"{Message} {Notification}"
    return Message
  except:
    await DMHelper.DMUser(ctx, "Something went wrong tagging one of the users.")
    return

# Helper function to tag a single user
async def NotifyUser(ctx, userid):
  try:
    Message = f"<@!{userid}>"
    return Message
  except:
    await DMHelper.DMUser(ctx, "Something went wrong tagging the user.")
    return
