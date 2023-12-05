import sqlite3
import asyncio
import discord
from discord import ChannelType
from Helpers import DateTimeFormatHelper
from Helpers import DMHelper

# Helper function to join reserves
async def JoinReserves(bot, message, JoinedUserDisplayName, Description, LocalDate, Origin, UserID, RaidID, RoleID, RoleName):
  try:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()
    c.execute("INSERT INTO RaidReserves (Origin, UserID, RaidID, RoleID) VALUES (?, ?, ?, ?)", (Origin, UserID, RaidID, RoleID))
    conn.commit()
    conn.close()
    LocalDate = await DateTimeFormatHelper.LocalToUnixTimestamp(LocalDate)
    await message.channel.send(f"{JoinedUserDisplayName} has joined the party {Description} on {LocalDate} as a reserve {RoleName}!")
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong adding you to the reserves")
    conn.close()
    return

# Helper function to withdraw from reserves
async def WithdrawFromReserves(bot, message, JoinedUserDisplayName, Description, LocalDate, Origin, UserID, RaidID):
  try:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()
    c.execute("DELETE FROM RaidReserves WHERE Origin = (?) AND RaidID = (?) and UserID = (?)", (Origin, RaidID, UserID,))
    conn.commit()
    conn.close()
    LocalDate = await DateTimeFormatHelper.LocalToUnixTimestamp(LocalDate)
    await message.channel.send(f"{JoinedUserDisplayName} has withdrawn from the reserves for the party {Description} on {LocalDate}!")
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong removing you from the reserves")
    conn.close()
    return

# Helper function to check reserves
async def CheckReserves(bot, message, JoinedUserDisplayName, Description, LocalDate, Origin, UserID, RaidID, RoleName, RoleID):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author.id == UserID

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute("SELECT ID FROM RaidReserves WHERE RaidID = (?) AND UserID = (?)", (RaidID, UserID))
  row = c.fetchone()
  if row:
    await DMHelper.DMUserByID(bot, UserID, "You're already on the reserves list for this run would you like to withdraw from the reserves? (Y/N).")
    WithdrawFromReserve = None
    while not WithdrawFromReserve:
      try:
        WithdrawFromReserveResponse = await bot.wait_for(event='message', timeout=60, check=DMCheck)
        if WithdrawFromReserveResponse.content in("Y","y","Yes","yes"):
          WithdrawFromReserve = "yes"
          await WithdrawFromReserves(bot, message, JoinedUserDisplayName, Description, LocalDate, Origin, UserID, RaidID)
          conn.close()
        elif WithdrawFromReserveResponse.content in("N","n","No","no"):
          WithdrawFromReserve = "no"
          conn.close()
        else:
          await DMHelper.DMUserByID(bot, UserID, "Invalid answer detected, please respond with yes or no.")
          continue
      except asyncio.TimeoutError:
        conn.close()
        await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again if you still wish to withdraw from the reserves for this run.")
        return
  if not row:
    await DMHelper.DMUserByID(bot, UserID, f"This run already has the required number of {RoleName}, would you like to be put on the reserve list? (Y/N).")
    Reserve = None
    while not Reserve:
      try:
        ReserveResponse = await bot.wait_for(event='message', timeout=60, check=DMCheck)
        if ReserveResponse.content in("Y","y","Yes","yes"):
          Reserve = "yes"
          await JoinReserves(bot, message, JoinedUserDisplayName, Description, LocalDate, Origin, UserID, RaidID, RoleID, RoleName)
          conn.close()
        elif ReserveResponse.content in("N","n","No","no"):
          Reserve = "no"
          conn.close()
        else:
          await DMHelper.DMUserByID(bot, UserID, "Invalid answer detected, please respond with yes or no.")
          continue
      except asyncio.TimeoutError:
        conn.close()
        await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again if you still wish to join the reserves for this run.")
        return

async def DeleteFromReserves(RaidID, UserID):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute("DELETE FROM RaidReserves where RaidID = (?) AND UserID = (?)", (RaidID, UserID,))
  conn.commit()
  conn.close()
  return