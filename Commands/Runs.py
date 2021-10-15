import sqlite3
import re
from datetime import datetime
from discord_components import *
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleIconHelper
from Helpers import DMHelper
from Helpers import DateTimeValidationHelper
from Helpers import ReactionHelper
from Helpers import RaidIDHelper
from Helpers import ButtonInteractionHelper

async def ListRunsOnDate(message, bot):

  # Get Origin
  Origin = await OriginHelper.GetOrigin(message)

  if not Origin:
    return

  if message.content == '!runs':
    await DMHelper.DMUser(message, "Incomplete command received, please provide the date as well")
    return

  # Open connection to DB
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # split message input
  splitmessage = str.split(message.content, ' ')
  date = splitmessage[1]

  # Check if date provided matches dd-mm-yyyy format
  pattern = re.compile(r'(\d{2})-(\d{2})-(\d{4})')
  match = pattern.match(date)

  # Convert to sqlite date format
  if match:
    splitdate = str.split(date, '-')
    day = splitdate[0]
    month = splitdate[1]
    year = splitdate[2]
    sqlitedate = f"{year}-{month}-{day}"

    # Check if date is not in the past
    try:
      current_date = datetime.utcnow().strftime("%Y-%m-%d")
      if sqlitedate < current_date:
        await DMHelper.DMUser(message, "It's not possible to search on dates in the past")
        conn.close()
        # Delete message that contains command
        await message.delete()
        return
    except ValueError:
      await DMHelper.DMUser(message, "Unable to convert date from local to sqlite format")
      conn.close()
      return

    try:
      TankIcon = await RoleIconHelper.GetTankIcon()
      DpsIcon = await RoleIconHelper.GetDpsIcon()
      HealerIcon = await RoleIconHelper.GetHealerIcon()
    except ValueError:
      await DMHelper.DMUser(message, "Something went wrong retrieving role icons")
      conn.close()
      return

    # Execute query
    try:
      ChannelID = message.channel.id
      c.execute("SELECT ID, Name, OrganizerUserID, Status, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfhealersSignedUp, Date FROM Raids WHERE Date like (?) AND Origin = (?) AND Status != 'Cancelled' AND ChannelID = (?) ORDER BY Date ASC, ID ASC", (sqlitedate+'%', Origin, ChannelID))
    except ValueError:
      await DMHelper.DMUser(message, "Run not found")
      conn.close()
      return

    # Delete message that contains command
    await message.delete()

    rows = c.fetchall()

    if rows:
      # Header message
      await message.channel.send(f"The following runs are planned on {date}:\n")

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
          SplitDate = str.split(Date, ' ')
          Date = SplitDate[0]
          Time = SplitDate[1]

          # Split date into day, month and year values
          splitdate = Date.split('-')
          day = splitdate[2]
          month = splitdate[1]
          year = splitdate[0]

          # Generate date in sqlite format
          LocalTime = f"{day}-{month}-{year} {Time}"

          try:
            OrganizerName = await UserHelper.GetDisplayName(message, OrganizerUserID, bot)
          except ValueError:
            await DMHelper.DMUser(message, "Something went wrong getting the display name of the organizer, perhaps they have left the server")
            conn.close()
            return

        except IndexError:
          await DMHelper.DMUser(message, "Unable to convert variables")
          conn.close()
          return

        if OrganizerName:
          await message.channel.send(f"**Run:** {ID}\n**Description:** {Name}\n**Organizer:** {OrganizerName}\n**Date (UTC):** {LocalTime}\n**Status:** {Status}\n{TankIcon} {NrOfTanksSignedUp}\/{NrOfTanksRequired} {DpsIcon} {NrOfDpsSignedUp}\/{NrOfDpsRequired} {HealerIcon} {NrOfhealersSignedUp}\/{NrOfHealersRequired}",components=[[Button(style=ButtonStyle.blue, label="Tank", custom_id="tank_btn"),Button(style=ButtonStyle.red, label="DPS", custom_id="dps_btn"),Button(style=ButtonStyle.green, label="Healer", custom_id="healer_btn"),Button(style=ButtonStyle.grey, label="Rally", custom_id="rally_btn")],[Button(style=ButtonStyle.grey, label="Members", custom_id="members_btn"),Button(style=ButtonStyle.grey, label="Reserves", custom_id="reserves_btn")],[Button(style=ButtonStyle.grey, label="Edit description", custom_id="editdesc_btn"),Button(style=ButtonStyle.grey, label="Reschedule", custom_id="reschedule_btn"),Button(style=ButtonStyle.red, label="Cancel", custom_id="cancel_btn")]])

    else:
       await message.channel.send(f"No runs found on {date}")
       conn.close()
       return

  else:
    await DMHelper.DMUser(message, "Invalid date and time detected please use the dd-mm-yyyy format")
    conn.close()
    return

  # Close the connection
  conn.close()
  return
