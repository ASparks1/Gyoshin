import asyncio
import sqlite3
import discord
from discord import ChannelType
from Helpers import DateTimeFormatHelper
from Helpers import DMHelper
from Helpers import DismissHelper
from Helpers import MemberHelper
from Helpers import MessageHelper
from Helpers import RaidIDHelper
from Helpers import UserHelper

async def DismissMembers(bot, message, UserID):
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
      c.execute("SELECT Name, Date FROM Raids WHERE ID = (?)", (RaidID,))
      row = c.fetchone()
      RaidName = row[0]
      Date = row[1]
      LocalDate = await DateTimeFormatHelper.SqliteToLocalNoCheck(Date)
      conn.close()
      # Converting tuple result into list for later use
      RaidMembers = [int(x) for x, in RaidMembers]
      await MemberHelper.ListMembersForOrganizer(message, bot, UserID)
    else:
      conn.close()
      await DMHelper.DMUserByID(bot, UserID, "Only the organizer of this run is allowed to dismiss members.")
      return
  except:
    conn.close()
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving raid members")
    return

  if RaidMembers:
    MembersToDismiss = None
    while not MembersToDismiss:
      await DMHelper.DMUserByID(bot, UserID, "Please enter the number(s) of the member(s) you want to dismiss separated by spaces if you want to dismiss more then 1 member.")
      try:
        response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      except asyncio.TimeoutError:
        await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again from the channel if you still want to dismiss members from this run.")
        return

      try:
        MembersToDismiss = response.content
        MembersToDismiss = str.split(MembersToDismiss, ' ')
        MembersToDismissMessage = None
        for MemberToDismiss in MembersToDismiss:
          MemberToDismissNumber = int(MemberToDismiss[0])
          MemberToDismissIndex = MemberToDismissNumber - 1
          MemberToDismiss = RaidMembers[MemberToDismissIndex]
          MemberToDismissDisplayName = await UserHelper.GetDisplayName(message, MemberToDismiss, bot)
          if MembersToDismissMessage:
            MembersToDismissMessage = f"{MembersToDismissMessage} and {MemberToDismissDisplayName}"
            DismissMessage = "have been dismissed"
          if not MembersToDismissMessage:
            MembersToDismissMessage = MemberToDismissDisplayName
            DismissMessage = "has been dismissed"
      except:
        await DMHelper.DMUserByID(bot, UserID, "Please enter valid number(s).")
        continue

    CanDismiss = None
    while not CanDismiss:
      try:
        LocalDateDisplay = await DateTimeFormatHelper.LocalToUnixTimestamp(LocalDate)
        await DMHelper.DMUserByID(bot, UserID, f"Do you want to dismiss {MembersToDismissMessage} from {RaidName} on {LocalDateDisplay}? (Y/N)")
        response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
        if response.content in("Y","y","Yes","yes"):
          CanDismiss = 'yes'
          for MemberToDismiss in MembersToDismiss:
            MemberToDismissNumber = int(MemberToDismiss[0])
            MemberToDismissIndex = MemberToDismissNumber - 1
            MemberToDismiss = RaidMembers[MemberToDismissIndex]
            await DismissHelper.DismissMember(bot, RaidID, MemberToDismiss, UserID)
          UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID)
          if UpdatedMessage:
            await message.edit(content=UpdatedMessage)
          await message.channel.send(f"{MembersToDismissMessage} {DismissMessage} from {RaidName} on {LocalDateDisplay}.")
        elif response.content in("N","n","No","no"):
          CanDismiss = "no"
          return
        else:
          await DMHelper.DMUserByID(bot, UserID, "Invalid answer detected, please respond with yes or no.")
          continue
      except asyncio.TimeoutError:
        await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again from the channel if you still want to dismiss members for this run.")
        return
