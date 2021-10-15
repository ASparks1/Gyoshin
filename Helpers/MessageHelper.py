import sqlite3
from Helpers import RaidIDHelper
from Helpers import DMHelper
from Helpers import RoleIconHelper
from Helpers import UserHelper

async def UpdateRaidInfoMessage(message, bot, UserID, Origin):
  try:
    RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)
  except:
    await DMHelper.DMUserByID(bot, UserID, f"Something went wrong obtaining the run information.")
    return
    
  try:
    TankIcon = await RoleIconHelper.GetTankIcon(bot, 'Tank')
    DpsIcon = await RoleIconHelper.GetDpsIcon(bot, 'Dps')
    HealerIcon = await RoleIconHelper.GetHealerIcon(bot, 'Healer')
  except:
    await DMHelper.DMUserByID(bot, UserID, f"Something went wrong retrieving role icons")
    return
    
  if RaidID:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()
    
    try:
      c.execute(f"SELECT ID, Name, OrganizerUserID, Status, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfhealersSignedUp, Date FROM Raids WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
      
      row = c.fetchone()
      
      if row:
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
          await DMHelper.DMUserByID(bot, UserID, f"Something went wrong getting the display name of the organizer, perhaps they have left the server")
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