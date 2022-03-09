from Helpers import DMHelper

# Helper function to obtain the run number from the message
async def GetRaidIDFromMessage(ctx):
  try:
    messagelines = ctx.content.splitlines()
    splitword = 'Run:** '
    RaidID = int(messagelines[0].partition(splitword)[2])
    return RaidID
  except:
    await DMHelper.DMUser(ctx, "Something went wrong obtaining the run number.")
    return
