import sqlite3
import re
import discord
from datetime import datetime
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleIconHelper
from Helpers import DMHelper
from Helpers import DateTimeValidationHelper
from Helpers import DateTimeFormatHelper
from Helpers import ReactionHelper
from Helpers import RaidIDHelper
from Helpers import ButtonInteractionHelper
from Helpers import MyRunsHelper

async def ListMyRunsHelper(ctx, bot, RunType):
  UserID = ctx.author.id
  if not UserID:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong getting user information")
    return

  try:
    TankIcon = await RoleIconHelper.GetTankIcon()
    DpsIcon = await RoleIconHelper.GetDpsIcon()
    HealerIcon = await RoleIconHelper.GetHealerIcon()
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving role icons")
    return

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    current_date = discord.utils.utcnow().strftime("%Y-%m-%d %H:%M")
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong getting the current date and time")
    conn.close()
    return

  try:
    if RunType == 'MyRuns':
      c.execute("SELECT ID, Name, OrganizerUserID, Status, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfhealersSignedUp, Date, Origin FROM Raids WHERE ID IN (SELECT RaidID FROM RaidMembers WHERE UserID = (?)) AND Date >= (?) AND Status != 'Cancelled' ORDER BY Date ASC", (UserID, current_date,))
    elif RunType == 'MyReserveRuns':
      c.execute("SELECT ID, Name, OrganizerUserID, Status, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfhealersSignedUp, Date, Origin FROM Raids WHERE ID IN (SELECT RaidID FROM RaidReserves WHERE UserID = (?)) AND Date >= (?) AND Status != 'Cancelled' ORDER BY Date ASC", (UserID, current_date,))
  except:
    await DMHelper.DMUserByID(bot, UserID, "Run not found")
    conn.close()
    return

  rows = c.fetchmany(5)
  if not rows:
    if RunType == 'MyRuns':
      await DMHelper.DMUserByID(bot, UserID, "You have no upcoming runs")
      conn.close()
    elif RunType == 'MyReserveRuns':
      await DMHelper.DMUserByID(bot, UserID, "You are not on the reserve list for any upcoming runs")
      conn.close()

  if rows:
    Message = None
    for row in rows:
      try:
        ID = row[0]
        Name = row[1]
        OrganizerUserID = row[2]
        Status = row[3]
        NrOfTanksRequired = row[4]
        NrOfTanksSignedUp = row[5]
        NrOfDpsRequired = row[6]
        NrOfDpsSignedUp = row[7]
        NrOfHealersRequired = row[8]
        NrOfhealersSignedUp = row[9]
        Date = row[10]
        Origin = row[11]
        LocalDate = await DateTimeFormatHelper.SqliteToLocalNoCheck(Date)
        LocalDateDisplay = await DateTimeFormatHelper.LocalToUnixTimestamp(LocalDate)
        try:
          guild = bot.get_guild(Origin)
          member_obj = await guild.fetch_member(OrganizerUserID)
        except:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving this users display name, perhaps they have left the server")
        try:
          if member_obj:
            OrganizerName = member_obj.display_name
        except:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong getting the display name of the organizer, perhaps they have left the server")
          conn.close()
          return
      except:
        await DMHelper.DMUserByID(bot, UserID, "Unable to convert variables")
        conn.close()
        return

      if OrganizerName:
        RunMessage = f"**Run:** {ID}\n**Description:** {Name}\n**Server:** {guild}\n**Organizer:** {OrganizerName}\n**Date:** {LocalDateDisplay}\n**Status:** {Status}\n{TankIcon} {NrOfTanksSignedUp}\/{NrOfTanksRequired} {DpsIcon} {NrOfDpsSignedUp}\/{NrOfDpsRequired} {HealerIcon} {NrOfhealersSignedUp}\/{NrOfHealersRequired}\n"
        if not Message:
          if RunType == 'MyRuns':
            Message = f"You have signed up for the following run(s):\n{RunMessage}"
          elif RunType == 'MyReserveRuns':
            Message = f"You are on the reserves list for the following run(s):\n{RunMessage}"
        elif Message:
          RunMessage = f"**Run:** {ID}\n**Description:** {Name}\n**Server:** {guild}\n**Organizer:** {OrganizerName}\n**Date:** {LocalDateDisplay}\n**Status:** {Status}\n{TankIcon} {NrOfTanksSignedUp}\/{NrOfTanksRequired} {DpsIcon} {NrOfDpsSignedUp}\/{NrOfDpsRequired} {HealerIcon} {NrOfhealersSignedUp}\/{NrOfHealersRequired}\n"
          Message = f"{Message}{RunMessage}"

    await DMHelper.DMUserByID(bot, UserID, f"{Message}")
    conn.close()
    return
