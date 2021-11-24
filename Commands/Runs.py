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

async def ListRunsOnDate(message, bot):
  Origin = await OriginHelper.GetOrigin(message)
  if not Origin:
    return

  if message.content == '!runs':
    await DMHelper.DMUser(message, "Incomplete command received, please provide the date as well")
    return

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  splitmessage = str.split(message.content, ' ')
  date = splitmessage[1]
  pattern = re.compile(r'(\d{2})-(\d{2})-(\d{4})')
  match = pattern.match(date)

  if match:
    splitdate = str.split(date, '-')
    day = splitdate[0]
    month = splitdate[1]
    year = splitdate[2]
    sqlitedate = f"{year}-{month}-{day}"

    try:
      current_date = datetime.utcnow().strftime("%Y-%m-%d")
      if sqlitedate < current_date:
        await DMHelper.DMUser(message, "It's not possible to search on dates in the past")
        conn.close()
        await message.delete()
        return
    except:
      await DMHelper.DMUser(message, "Unable to convert date from local to sqlite format")
      conn.close()
      return

    try:
      TankIcon = await RoleIconHelper.GetTankIcon()
      DpsIcon = await RoleIconHelper.GetDpsIcon()
      HealerIcon = await RoleIconHelper.GetHealerIcon()
    except:
      await DMHelper.DMUser(message, "Something went wrong retrieving role icons")
      conn.close()
      return

    try:
      ChannelID = message.channel.id
      c.execute("SELECT ID, Name, OrganizerUserID, Status, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfhealersSignedUp, Date FROM Raids WHERE Date like (?) AND Origin = (?) AND Status != 'Cancelled' AND ChannelID = (?) ORDER BY Date ASC, ID ASC", (sqlitedate+'%', Origin, ChannelID))
    except:
      await DMHelper.DMUser(message, "Run not found")
      conn.close()
      return

    await message.delete()
    rows = c.fetchall()
    if rows:
      await message.channel.send(f"The following runs are planned on {date}:\n")

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
          LocalDate = await DateTimeFormatHelper.SqliteToLocalNoCheck(Date)
          try:
            OrganizerName = await UserHelper.GetDisplayName(message, OrganizerUserID, bot)
          except:
            await DMHelper.DMUser(message, "Something went wrong getting the display name of the organizer, perhaps they have left the server")
            conn.close()
            return

        except:
          await DMHelper.DMUser(message, "Unable to convert variables")
          conn.close()
          return

        if OrganizerName:
          await message.channel.send(f"**Run:** {ID}\n**Description:** {Name}\n**Organizer:** {OrganizerName}\n**Date (UTC):** {LocalDate}\n**Status:** {Status}\n{TankIcon} {NrOfTanksSignedUp}\/{NrOfTanksRequired} {DpsIcon} {NrOfDpsSignedUp}\/{NrOfDpsRequired} {HealerIcon} {NrOfhealersSignedUp}\/{NrOfHealersRequired}",components=[[Button(style=ButtonStyle.blue, label="Tank", custom_id="tank_btn"),Button(style=ButtonStyle.red, label="DPS", custom_id="dps_btn"),Button(style=ButtonStyle.green, label="Healer", custom_id="healer_btn"),Button(style=ButtonStyle.grey, label="Rally", custom_id="rally_btn")],[Button(style=ButtonStyle.grey, label="Members", custom_id="members_btn"),Button(style=ButtonStyle.grey, label="Reserves", custom_id="reserves_btn"),Button(style=ButtonStyle.grey, label="Message members", custom_id="messageraidmembers_btn")],[Button(style=ButtonStyle.grey, label="Edit description", custom_id="editdesc_btn"),Button(style=ButtonStyle.grey, label="New organizer", custom_id="neworganizer_btn"),Button(style=ButtonStyle.grey, label="Reschedule", custom_id="reschedule_btn"),Button(style=ButtonStyle.red, label="Cancel", custom_id="cancel_btn")]])

    else:
       await message.channel.send(f"No runs found on {date}")
       conn.close()
       return
  else:
    await DMHelper.DMUser(message, "Invalid date and time detected please use the dd-mm-yyyy format")
    conn.close()
    return

  conn.close()
  return
