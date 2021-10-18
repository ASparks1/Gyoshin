import asyncio
import sqlite3
import discord
from discord import ChannelType
from Helpers import DMHelper
from Helpers import MemberHelper
from Helpers import RoleHelper
from Helpers import UserHelper

# Helper function for reschedule command to reduce the amount nested blocks in main function
async def Reschedule(bot, message, UserID, RaidID, RaidName, LocalOldDate, NewDate, sqlitenewdate, GuildName):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  RescheduleRun = None
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author.id == UserID

  while not RescheduleRun:
    await DMHelper.DMUserByID(bot, UserID, f"Do you want to reschedule the run {RaidName} from {LocalOldDate} to {NewDate} in the {GuildName} server (Y/N)?")
    try:
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      if response.content == "Y" or response.content == "y" or response.content == "Yes" or response.content == "yes":
        RescheduleRun = "yes"
      elif response.content == "N" or response.content == "n" or response.content == "No" or response.content == "no":
        RescheduleRun = "no"
      else:
        await DMHelper.DMUserByID(bot, UserID, "Please enter a valid response of yes or no.")
        continue
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again from the channel if you still want to reschedule this run.")
      conn.close()
      return

  if RescheduleRun == "yes":
    try:
      RescheduleNotifications = await MemberHelper.CheckForMembersBesidesOrganizer(bot, message, RaidID, UserID)
    except:
     await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving raid members")
     conn.close()
     return

    try:
      c.execute("DELETE FROM RaidMembers WHERE RaidID = (?) AND UserID != (?)", (RaidID, UserID,))
      c.execute("DELETE FROM RaidReserves WHERE RaidID = (?)", (RaidID,))
    except:
      conn.close()
      return

    try:
      c.execute("SELECT RoleID FROM RaidMembers WHERE RaidID = (?) AND UserID = (?)", (RaidID, UserID,))
      row = c.fetchone()
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining the role of the organizer")
      conn.close()
      return

    if not row:
      await DMHelper.DMUserByID(bot, UserID, "Unable to find role of the creator of this run")
      conn.close()
      return

    RoleID = row[0]
    if not RoleID:
      await DMHelper.DMUserByID(bot, UserID, "Unable to retrieve role id")
      conn.close()
      return

    RoleName = await RoleHelper.GetRoleName(RoleID)
    if not RoleName:
      await DMHelper.DMUserByID(bot, UserID, "Unable to resolve role name")
      conn.close()
      return

    if RoleName == 'tank':
      try:
        c.execute("Update Raids SET Date = (?), NrOfPlayersSignedUp = (?), NrOfTanksSignedUp = (?), NrOfDpsSignedUp = (?), NrOfHealersSignedUp = (?), Status = 'Forming' WHERE ID = (?)", (sqlitenewdate, 1, 1, 0, 0, RaidID,))
        conn.commit()
      except:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of players and tanks")
        conn.close()
        return

    if RoleName == 'dps':
      try:
        c.execute("Update Raids SET Date = (?), NrOfPlayersSignedUp = (?), NrOfTanksSignedUp = (?), NrOfDpsSignedUp = (?), NrOfHealersSignedUp = (?), Status = 'Forming' WHERE ID = (?)", (sqlitenewdate, 1, 0, 1, 0, RaidID,))
        conn.commit()
      except:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of players and dps")
        conn.close()
        return

    if RoleName == 'healer':
      try:
        c.execute("Update Raids SET Date = (?), NrOfPlayersSignedUp = (?), NrOfTanksSignedUp = (?), NrOfDpsSignedUp = (?), NrOfHealersSignedUp = (?), Status = 'Forming' WHERE ID = (?)", (sqlitenewdate, 1, 0, 0, 1, RaidID,))
        conn.commit()
      except:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of players and healers")
        conn.close()
        return

    try:
      conn.commit()
      UserName = await UserHelper.GetDisplayName(message, UserID, bot)

      if RescheduleNotifications:
        await message.channel.send(f"{RescheduleNotifications}\n{UserName} has rescheduled the run {RaidName} from {LocalOldDate} to {NewDate}, if you were signed up to this run please sign up again on the new date if you can.")
      elif not RescheduleNotifications:
        await message.channel.send(f"{UserName} has rescheduled the run {RaidName} from {LocalOldDate} to {NewDate}.")

      await message.delete()
      conn.close()
      return
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong rescheduling the run")
      conn.close()
      return
