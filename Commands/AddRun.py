from Helpers import AddRunHelper
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import DMHelper
from Commands import Templates

async def AddRunInDM(ctx, bot):
  try:
    UserID = ctx.author.id
    Origin = await OriginHelper.GetOrigin(ctx, bot, UserID)
    GuildName = await OriginHelper.GetName(ctx, bot, UserID)    
    CreatorDisplay = await UserHelper.GetDisplayName(ctx, UserID, bot)
    ChannelID = ctx.channel.id
  except:
     await DMHelper.DMUserByID(bot, UserID, "Something went wrong when gathering server and user information.")
     return

  try:
    Name = await AddRunHelper.GetRunName(bot, ctx, UserID, CreatorDisplay, GuildName)
    if Name:
      DateTime = await AddRunHelper.GetRunDateTime(bot, ctx, UserID)
    else:
      return
    if DateTime:
      sqldatetime = await DateTimeFormatHelper.LocalToSqlite(ctx, DateTime)
    else:
      return
    if sqldatetime:
      await Templates.GetTemplates(ctx, bot)
      UsingTemplate = await AddRunHelper.UseTemplateQuestion(bot, ctx, UserID, Origin)
    else:
      return
  except:
    print("Unable to continue with creating run user did not provide all required information in time")
    return

  if UsingTemplate == 'yes':
    await AddRunHelper.UseTemplateToCreateRun(bot, ctx, UserID, Origin, CreatorDisplay, ChannelID, Name, DateTime, sqldatetime)
  else:
    ValidNrOfPlayers = None
    try:
      while not ValidNrOfPlayers:
        NrOfPlayers = await AddRunHelper.GetNrOfPlayers(bot, ctx, UserID)
        NrOfTanks = await AddRunHelper.GetNrOfTanks(bot, ctx, UserID)
        NrOfDps = await AddRunHelper.GetNrOfDPS(bot, ctx, UserID)
        NrOfHealers = await AddRunHelper.GetNrOfHealers(bot, ctx, UserID)

        if NrOfPlayers != NrOfTanks + NrOfDps + NrOfHealers:
          await DMHelper.DMUserByID(bot, UserID, "Please ensure the total of each role equals the total number of players required.")
        else:
          ValidNrOfPlayers = "yes"

      RoleID = await AddRunHelper.GetOrganizerRoleID(bot, ctx, UserID, NrOfTanks, NrOfDps, NrOfHealers)
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
      Confirm = await AddRunHelper.SummarizeRunInfoForConfirmation(bot, ctx, UserID, Name, DateTime, NrOfTanks, NrOfHealers, NrOfDps)

      if Confirm == "yes":
        await AddRunHelper.CreateRun(bot, ctx, UserID, Name, Origin, sqldatetime, NrOfPlayers, NrOfTanks, NumberOfCurrentTanks, NrOfDps, NumberOfCurrentDps, NrOfHealers, NumberOfCurrentHealers, Status, ChannelID, RoleID, CreatorDisplay, DateTime)
      if Confirm == "no":
        await DMHelper.DMUserByID(bot, UserID, "Your request to create a run has been cancelled, please call the command again in the relevant channel if you wish to try again.")
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong setting your role and the number of other roles required.")
      return
