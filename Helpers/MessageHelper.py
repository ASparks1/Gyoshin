import sqlite3
import asyncio
import discord
from discord import ChannelType
from Helpers import RaidIDHelper
from Helpers import DMHelper
from Helpers import RoleIconHelper
from Helpers import UserHelper
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper

# Helper function to get updated information message back
async def UpdateRaidInfoMessage(message, bot, UserID):
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
      c.execute("SELECT Name, OrganizerUserID, Status, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfhealersSignedUp, Date FROM Raids WHERE ID = (?)", (RaidID,))
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
        LocalDate = await DateTimeFormatHelper.SqliteToLocalNoCheck(Date)
        try:
          OrganizerName = await UserHelper.GetDisplayName(message, OrganizerUserID, bot)
        except:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong getting the display name of the organizer, perhaps they have left the server")
          conn.close()
          return

        if OrganizerName:
          UpdatedMessage = f"**Run:** {RaidID}\n**Description:** {Name}\n**Organizer:** {OrganizerName}\n**Date (UTC):** {LocalDate}\n**Status:** {Status}\n{TankIcon} {NrOfTanksSignedUp}\/{NrOfTanksRequired} {DpsIcon} {NrOfDpsSignedUp}\/{NrOfDpsRequired} {HealerIcon} {NrOfhealersSignedUp}\/{NrOfHealersRequired}"

        conn.close()
        return UpdatedMessage
      else:
        conn.close()
        return
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong trying to retrieve run {RaidID}")
      conn.close()
      return UpdatedMessage

# Helper function to send a message to raidmembers
async def MessageRaidMembers(message, bot, UserID):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author.id == UserID

  try:
    RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)
    OrganizerName = await UserHelper.GetDisplayName(message, UserID, bot)
    GuildName = await OriginHelper.GetName(message)
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining the run information.")
    return

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    c.execute("SELECT OrganizerUserID, Name, Date FROM Raids WHERE ID = (?)", (RaidID,))
    row = c.fetchone()
    OrganizerUserID = row[0]
    RaidName = row[1]
    Date = row[2]
    LocalDate = await DateTimeFormatHelper.SqliteToLocalNoCheck(Date)
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to retrieve run information")
    conn.close()
    return

  if UserID != OrganizerUserID:
    await DMHelper.DMUserByID(bot, UserID, "Only the organizer is allowed to send messages to raidmembers")
    conn.close()
    return

  c.execute("SELECT UserID FROM RaidMembers WHERE RaidID = (?) AND UserID != (?)", (RaidID, UserID,))
  rows = c.fetchall()
  if rows:
    try:
      await DMHelper.DMUserByID(bot, UserID, f"Please provide the message you want to send to the members of {RaidName} on {LocalDate} in the {GuildName} Server")
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      MessageToSend = response.content
      MessageToSend = f"{OrganizerName} is messaging you the following from {RaidName} on {LocalDate} from the {GuildName} server:\n{MessageToSend}"
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again from the channel if you still want to reschedule this run.")
      conn.close()
      return

    for row in rows:
      try:
        MemberID = row[0]
        await DMHelper.DMUserByID(bot, MemberID, MessageToSend)
      except:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to send the message")
        conn.close()
        return
    await DMHelper.DMUserByID(bot, UserID, "Message sent!")
    conn.close()
    return

  if not rows:
    await DMHelper.DMUserByID(bot, UserID, "There are no members to message for this run")
    conn.close()
    return
