from Helpers import DMHelper

# Helper function to obtain the run number from the message
async def GetRaidIDFromMessage(message):
  try:
    messagelines = message.content.splitlines()
    splitword = 'Run:** '
    RaidID = int(messagelines[0].partition(splitword)[2])
    return RaidID
  except:
    await DMHelper.DMUser(message, "Something went wrong obtaining the run number.")
    return
