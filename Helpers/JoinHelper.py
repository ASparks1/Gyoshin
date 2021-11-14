import asyncio
import sqlite3
from Commands import Withdraw
from Helpers import DMHelper
from Helpers import MessageHelper
from Helpers import NotificationHelper

# Helper function to notify organizer when all slots have been filled
async def NotifyOrganizer(message, bot, UserID, RaidID, Organizer, Description, LocalDate):
  try:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()
    c.execute("SELECT NrOfPlayersRequired, NrOfPlayersSignedUp FROM Raids  WHERE ID = (?)", (RaidID,))
    row = c.fetchone()

    if row:
      NrOfPlayersRequired = row[0]
      NrOfPlayersSignedUp = row[1]

    if NrOfPlayersRequired == NrOfPlayersSignedUp:
      try:
        c.execute("UPDATE Raids SET Status = 'Formed' WHERE ID = (?)", (RaidID,))
        try:
          conn.commit()
          conn.close()
          UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID)
          await message.edit(content=UpdatedMessage)
          NotifyOrganizerMessage = await NotificationHelper.NotifyUser(message, Organizer)
          await message.channel.send(f"{NotifyOrganizerMessage}\nYour crew for {Description} on {LocalDate} has been assembled!")
          return
        except:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong joining you to this run.")
          conn.close()
          return
      except:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating party status to formed.")
        conn.close()
        return
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of signed up players and dps")
    conn.close()
    return

# Helper function to allow a user to withdraw
async def Withdraw(message, bot, UserID, Description, LocalDate, GuildName, RoleNameSignedUpAs):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author.id == UserID

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  CanWithdraw = None
  while not CanWithdraw:
    await DMHelper.DMUserByID(bot, UserID, f"You have already joined the run {Description} on {LocalDate} in the {GuildName} server as a {RoleNameSignedUpAs}, would you like to withdraw from this run (Y/N)?")
    try:
      withdrawresponse = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      if withdrawresponse.content in("Y","y","Yes","yes"):
        CanWithdraw = "yes"
      elif withdrawresponse.content in("N","n","No","no"):
        CanWithdraw = "no"
      else:
        await DMHelper.DMUserByID(bot, UserID, "Invalid answer detected, please respond with yes or no.")
        continue
      except asyncio.TimeoutError:
        conn.close()
        await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again if you still wish to withdraw from the run.")
        return

  if CanWithdraw == "yes":
    await Withdraw.WithdrawFromRaid(message, bot, UserID)
    conn.close()
    return
  if CanWithdraw == "no":
    conn.close()
    return

# Helper function to allow a user to change role
async def ChangeRole(message, bot, UserID, Description, LocalDate, GuildName, RoleNameSignedUpAs, RoleName):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author.id == UserID

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  CanChangeRole = None
  while not CanChangeRole:
    await DMHelper.DMUserByID(bot, UserID, f"You have already joined the run {Description} on {LocalDate} in the {GuildName} server as a {RoleNameSignedUpAs}, would you like to change to {RoleName} for this run (Y/N)?")
    try:
      changeroleresponse = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      if changeroleresponse.content in("Y","y","Yes","yes"):
        CanChangeRole = "yes"
      elif changeroleresponse.content in("N","n","No","no"):
        CanChangeRole = "no"
      else:
        await DMHelper.DMUserByID(bot, UserID, "Invalid answer detected, please respond with yes or no.")
        continue
    except asyncio.TimeoutError:
      conn.close()
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again if you still wish to change your role for this run.")
      return

  if CanChangeRole == "yes":
    await ChangeRole.ChangeRole(message, bot, RoleName, UserID)
    conn.close()
    return
  if CanChangeRole == "no":
    conn.close()
    return