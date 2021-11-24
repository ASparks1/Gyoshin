import asyncio
import sqlite3
import discord
from discord import ChannelType
from Helpers import DateTimeFormatHelper
from Helpers import DMHelper
from Helpers import MemberHelper
from Helpers import MessageHelper
from Helpers import RaidIDHelper
from Helpers import UserHelper

# Function to appoint a new organizer
async def NewOrganizer(bot, message, UserID):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author.id == UserID

  try:
    RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining run information")
    return

  try:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()
    c.execute("SELECT OrganizerUserID FROM Raids WHERE ID = (?)",(RaidID,))
    row = c.fetchone()
    OrganizerUserID = row[0]
    if OrganizerUserID == UserID:
      c.execute("SELECT RM.UserID FROM RaidMembers RM JOIN Raids R on R.ID = RM.RaidID WHERE R.ID = (?) AND R.OrganizerUserID = (?) AND RM.UserID != (?)", (RaidID, UserID, UserID))
      RaidMembers = c.fetchall()
      conn.close()
      # Converting tuple result into list for later use
      RaidMembers = [int(x) for x, in RaidMembers]
      await MemberHelper.ListMembersForOrganizer(message, bot, UserID)
    else:
      conn.close()
      await DMHelper.DMUserByID(bot, UserID, "Only the organizer of this run is allowed to appoint a new organizer.")
      return
  except:
    conn.close()
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving raid members")
    return

  if RaidMembers:
    NewOrganizerDisplayName = None
    while not NewOrganizerDisplayName:
      await DMHelper.DMUserByID(bot, UserID, "Please enter the number of the member you want to promote to organizer.")
      try:
        response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
        try:
          NewOrganizerNumber = int(response.content)
          NewOrganizerIndex = NewOrganizerNumber - 1
          NewOrganizerUserID = RaidMembers[NewOrganizerIndex]
          NewOrganizerDisplayName = await UserHelper.GetDisplayName(message, NewOrganizerUserID, bot)
        except:
          await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
          continue
      except asyncio.TimeoutError:
        await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again from the channel if you still want to reschedule this run.")
        return

    CanPromote = None
    while not CanPromote:
      try:
        await DMHelper.DMUserByID(bot, UserID, f"Do you want to appoint {NewOrganizerDisplayName} as the new organizer of run {RaidID}? (Y/N)")
        response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
        if response.content in("Y","y","Yes","yes"):
          CanPromote = 'yes'
          conn = sqlite3.connect('RaidPlanner.db')
          c = conn.cursor()
          c.execute("SELECT Name, Date FROM Raids WHERE ID = (?)",(RaidID,))
          row = c.fetchone()
          RaidName = row[0]
          Date = row[1]
          LocalDate = await DateTimeFormatHelper.SqliteToLocalNoCheck(Date)
          c.execute("UPDATE Raids SET OrganizerUserID = (?) WHERE ID = (?)", (NewOrganizerUserID, RaidID,))
          conn.commit()
          conn.close()
          UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID)
          if UpdatedMessage:
            await message.edit(content=UpdatedMessage)
          await message.channel.send(f"{NewOrganizerDisplayName} is the new organizer of {RaidName} on {LocalDate}.")
        elif response.content in("N","n","No","no"):
          CanPromote = "no"
          return
        else:
          await DMHelper.DMUserByID(bot, UserID, "Invalid answer detected, please respond with yes or no.")
          continue
      except asyncio.TimeoutError:
        await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again from the channel if you still want to reschedule this run.")
        return
