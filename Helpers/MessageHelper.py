import sqlite3
from Helpers import RaidIDHelper
from Helpers import DMHelper
from Helpers import RoleIconHelper
from Helpers import UserHelper

async def UpdateRaidInfoMessage(message, bot, UserID, Origin):
  try:
    RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining the run information.")
    return

  try:
    TankIcon = await RoleIconHelper.GetTankIcon()
    DpsIcon = await RoleIconHelper.GetDpsIcon()
    HealerIcon = await RoleIconHelper.GetHealerIcon()
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving role icons")
    return

  if RaidID:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()

    try:
      c.execute("SELECT Name, OrganizerUserID, Status, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfhealersSignedUp, Date FROM Raids WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))

      row = c.fetchone()

      if row:
        Name = row[0]
        OrganizerUserID = row[1]
        Status = row[2]
        NrOfTanksRequired = row[3]
        NrOfTanksSignedUp = row[4]
        NrOfDpsRequired = row[5]
        NrOfDpsSignedUp = row[6]
        NrOfHealersRequired = row[7]
        NrOfhealersSignedUp = row[8]
        Date = row[9]

        # Split date into date and time values
        splitdate = Date.split(' ')
        Date = splitdate[0]
        Time = splitdate[1]

        # Split date into day, month and year values
        splitdate = Date.split('-')
        day = splitdate[2]
        month = splitdate[1]
        year = splitdate[0]

        # Split time into hours and minutes
        splittime = Time.split(':')
        hour = splittime[0]
        minute = splittime[1]

        # Generate date in sqlite format
        LocalTime = f"{day}-{month}-{year} {hour}:{minute}"

        try:
          OrganizerName = await UserHelper.GetDisplayName(message, OrganizerUserID, bot)
        except:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong getting the display name of the organizer, perhaps they have left the server")
          conn.close()
          return

        if OrganizerName:
          # Generate message
          UpdatedMessage = f"**Run:** {RaidID}\n**Description:** {Name}\n**Organizer:** {OrganizerName}\n**Date (UTC):** {LocalTime}\n**Status:** {Status}\n{TankIcon} {NrOfTanksSignedUp}\/{NrOfTanksRequired} {DpsIcon} {NrOfDpsSignedUp}\/{NrOfDpsRequired} {HealerIcon} {NrOfhealersSignedUp}\/{NrOfHealersRequired}"
        return UpdatedMessage
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong trying to retrieve run {RaidID}")
      conn.close()
      return UpdatedMessage
