from Helpers import AddRunHelper
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import DMHelper
from Commands import Templates

async def AddRunInDM(message, bot):
  try:
    Origin = await OriginHelper.GetOrigin(message)
    GuildName = await OriginHelper.GetName(message)
    UserID = message.author.id
    CreatorDisplay = await UserHelper.GetDisplayName(message, UserID, bot)
    ChannelID = message.channel.id
  except:
     await DMHelper.DMUserByID(bot, UserID, "Something went wrong when gathering server and user information.")
     return

  try:
    Name = await AddRunHelper.GetRunName(bot, message, UserID, CreatorDisplay, GuildName)
    if Name:
      DateTime = await AddRunHelper.GetRunDateTime(bot, message, UserID)
    else:
      return
    if DateTime:
      sqldatetime = await DateTimeFormatHelper.LocalToSqlite(message, DateTime)
    else:
      return
    if sqldatetime:
      await Templates.GetTemplates(message)
      UsingTemplate = await AddRunHelper.UseTemplateQuestion(bot, message, UserID, Origin)
    else:
      return
  except:
    print("Unable to continue with creating run user did not provide all required information in time")
    return

  if UsingTemplate == 'yes':
    await AddRunHelper.UseTemplateToCreateRun(bot, message, UserID, Origin, CreatorDisplay, ChannelID, Name, DateTime, sqldatetime)
  else:
    ValidNrOfPlayers = None
    while not ValidNrOfPlayers:
      NrOfPlayers = await AddRunHelper.GetNrOfPlayers(bot, message, UserID)
      NrOfTanks = await AddRunHelper.GetNrOfTanks(bot, message, UserID)
      NrOfDps = await AddRunHelper.GetNrOfDPS(bot, message, UserID)
      NrOfHealers = await AddRunHelper.GetNrOfHealers(bot, message, UserID)

      if NrOfPlayers != NrOfTanks + NrOfDps + NrOfHealers:
        await DMHelper.DMUserByID(bot, UserID, "Please ensure the total of each role equals the total number of players required.")
      else:
        ValidNrOfPlayers = "yes"

    RoleID = await AddRunHelper.GetOrganizerRoleID(bot, message, UserID, NrOfTanks, NrOfDps, NrOfHealers)
    if RoleID == 1:
      NumberOfCurrentTanks = 1
      NumberOfCurrentDps = 0
      NumberOfCurrentHealers = 0
    elif RoleID == 2:
      NumberOfCurrentDps = 1
      NumberOfCurrentTanks = 0
      NumberOfCurrentHealers = 0
    elif RoleID == 3:
      NumberOfCurrentHealers = 1
      NumberOfCurrentTanks = 0
      NumberOfCurrentDps = 0

    Status = await AddRunHelper.GetRunStatusToSet(NrOfPlayers)
    Confirm = await AddRunHelper.SummarizeRunInfoForConfirmation(bot, message, UserID, Name, DateTime, NrOfTanks, NrOfHealers, NrOfDps)

    if Confirm == "yes":
      await AddRunHelper.CreateRun(bot, message, UserID, Name, Origin, sqldatetime, NrOfPlayers, NrOfTanks, NumberOfCurrentTanks, NrOfDps, NumberOfCurrentDps, NrOfHealers, NumberOfCurrentHealers, Status, ChannelID, RoleID, CreatorDisplay, DateTime)
    if Confirm == "no":
      await DMHelper.DMUserByID(bot, UserID, "Your request to create a crew has been cancelled, please call the command again in the relevant channel if you wish to try again.")
