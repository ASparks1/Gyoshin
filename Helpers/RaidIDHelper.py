from Helpers import DMHelper

# Helper function to obtain the run number from the message
async def GetRaidIDFromMessage(message):
  try:
    # First split all lines of the message into their own object
    messagelines = message.content.splitlines() 
    # Add the partition word to split after
    splitword = 'Run:** '
    # Obtain the run number from the first line in case of create command
    RaidID = int(messagelines[0].partition(splitword)[2])
    if not RaidID:
      # Obtain the run number from the second line in case of runs command
      RaidID = messagelines[1].partition(splitword)[2]    
    return RaidID
  except:
    await DMHelper.DMUser(message, "Something went wrong obtaining the run number.")
    return