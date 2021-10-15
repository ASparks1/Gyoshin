import sqlite3
import re
from datetime import datetime
from discord_components import *
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleIconHelper
from Helpers import DMHelper
from Helpers import DateTimeValidationHelper
from Helpers import DateTimeFormatHelper
from Helpers import ReactionHelper
from Helpers import RaidIDHelper
from Helpers import ButtonInteractionHelper

async def ListMyRuns(message, bot):

  # Get user id
  UserID = message.author.id

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

  # Open connection to DB
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Get current date
  try:
    current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong getting the current date and time")
    conn.close()
    return

  # Execute query
  try:
    c.execute("SELECT ID, Name, OrganizerUserID, Status, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfhealersSignedUp, Date, Origin FROM Raids WHERE ID IN (SELECT RaidID FROM RaidMembers WHERE UserID = (?)) AND Date >= (?) AND Status != 'Cancelled' ORDER BY Date ASC", (UserID, current_date,))
  except:
    await DMHelper.DMUserByID(bot, UserID, "Run not found")
    conn.close()
    return

  rows = c.fetchmany(5)

  if not rows:
    await DMHelper.DMUserByID(bot, UserID, "You have no upcoming runs")
    conn.close()
    return

  if rows:
    # Start with an empty message
    Message = None
    # await DMHelper.DMUserByID(bot, UserID, f"You have signed up for the following runs:\n")

    for row in rows:

      # Data type conversions so variables can be used in message
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

        try:
          guild = bot.get_guild(Origin)
          # Get member object by discord user id
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
        await DMHelper.DMUser(message, "Unable to convert variables")
        conn.close()
        return

      if OrganizerName:
        # Post upcoming runs to DM
        RunMessage = f"**Run:** {ID}\n**Description:** {Name}\n**Server:** {guild}\n**Organizer:** {OrganizerName}\n**Date (UTC):** {LocalDate}\n**Status:** {Status}\n{TankIcon} {NrOfTanksSignedUp}\/{NrOfTanksRequired} {DpsIcon} {NrOfDpsSignedUp}\/{NrOfDpsRequired} {HealerIcon} {NrOfhealersSignedUp}\/{NrOfHealersRequired}\n"
        if not Message:
          Message = f"You have signed up for the following runs:\n{RunMessage}"
        elif Message:
          RunMessage = f"**Run:** {ID}\n**Description:** {Name}\n**Server:** {guild}\n**Organizer:** {OrganizerName}\n**Date (UTC):** {LocalDate}\n**Status:** {Status}\n{TankIcon} {NrOfTanksSignedUp}\/{NrOfTanksRequired} {DpsIcon} {NrOfDpsSignedUp}\/{NrOfDpsRequired} {HealerIcon} {NrOfhealersSignedUp}\/{NrOfHealersRequired}\n"
          Message = f"{Message}{RunMessage}"

    await DMHelper.DMUser(message, f"{Message}")

    # Close the connection
    conn.close()
    return
