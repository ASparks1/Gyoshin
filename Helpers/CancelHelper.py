import sqlite3
import asyncio
import discord
from Helpers import DMHelper
from Helpers import UserHelper
from Helpers import MemberHelper

# Helper function to cancel run
async def CancelRun(bot, message, Creator, UserID, RaidID, RaidName, LocalDate):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute("DELETE FROM RaidReserves WHERE RaidID = (?)", (RaidID,))
  c.execute("DELETE FROM RaidMembers WHERE RaidID = (?)", (RaidID,))
  c.execute("DELETE FROM Raids WHERE ID = (?)", (RaidID,))
  conn.commit()

  try:
    OrganizerDisplayName = await UserHelper.GetDisplayName(message, Creator, bot)
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong resolving the organizers' display name")
    conn.close()
    return

  CancelNotifications = await MemberHelper.CheckForMembersBesidesOrganizer(bot, message, RaidID, UserID)
  try:
    if CancelNotifications:
      await message.channel.send(f"{CancelNotifications}\n{OrganizerDisplayName} has cancelled the run {RaidName} on {LocalDate}.")
    elif not CancelNotifications:
      await message.channel.send(f"{OrganizerDisplayName} has cancelled the run {RaidName} on {LocalDate}.")

    await message.delete()
    conn.close()
    return
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong cancelling the run")
    conn.close()
    return
