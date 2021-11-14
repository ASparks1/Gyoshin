import re
import sqlite3
import asyncio
from discord import ChannelType
from Helpers import RoleHelper
from Helpers import UserHelper
from Helpers import NotificationHelper
from Helpers import OriginHelper
from Helpers import DMHelper
from Helpers import RaidIDHelper
from Helpers import MessageHelper
from Helpers import ReservesHelper
from Helpers import DateTimeFormatHelper
from Helpers import JoinHelper
from Commands import Withdraw
from Commands import ChangeRole

async def JoinRaid(message, bot, RoleName, UserID):
  try:
    RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong.")
    return

  try:
    RoleID = await RoleHelper.GetRoleID(RoleName)
  except:
    await DMHelper.DMUserByID(bot, UserID, "Invalid role, please enter a valid role, you can call !roles to see available roles.")
    return

  Origin = await OriginHelper.GetOrigin(message)
  GuildName = await OriginHelper.GetName(message)

  if not Origin or not UserID:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong resolving the user or server ID.")
    return

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    c.execute("SELECT ID, Name, Date, Origin, OrganizerUserID, NrOfPlayersRequired, NrOfPlayersSignedUp, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfHealersSignedUp, Status FROM Raids WHERE ID = (?)", (RaidID,))
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong when searching for this run.")
    conn.close()
    return

  try:
    row = c.fetchone()
  except:
    await DMHelper.DMUserByID(bot, UserID, f"I was not able to find run {RaidID}.")
    conn.close()
    return

  try:
    RaidID = row[0]
    Description = row[1]
    Date = row[2]
    LocalDate = await DateTimeFormatHelper.SqliteToLocalNoCheck(Date)
    Origin = row[3]
    Organizer = row[4]
    NrOfPlayersRequired = row[5]
    NrOfPlayersSignedUp = row[6]
    NrOfTanksRequired = row[7]
    NrOfTanksSignedUp = row[8]
    NrOfDpsRequired = row[9]
    NrOfDpsSignedUp = row[10]
    NrOfHealersRequired = row[11]
    NrOfHealersSignedUp = row[12]
    Status = row[13]
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving run information.")
    conn.close()
    return

  if Status == "Cancelled":
    await DMHelper.DMUserByID(bot, UserID, "This run does not have the status 'Forming', please ensure that you're not joining an already cancelled run.")
    conn.close()
    return

  # Ensure that the user is not trying to join a raid they have already joined
  c.execute("SELECT ID, RoleID FROM RaidMembers WHERE RaidID = (?) and UserID = (?)", (RaidID, UserID))
  usercheck = c.fetchone()

  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author.id == UserID

  if usercheck:
    try:
      RoleIDSignedUpAs = usercheck[1]
      RoleNameSignedUpAs = await RoleHelper.GetRoleName(RoleIDSignedUpAs)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining role information")
      conn.close()
      return

    # Offer to withdraw if user is signed up as this role
    if RoleID == RoleIDSignedUpAs:
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

    # Offer to change role if user is signed up with another role
    elif RoleID != RoleIDSignedUpAs:
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

  if not usercheck:
    JoinedUserDisplayName = await UserHelper.GetDisplayName(message, UserID, bot)
    # Update Raids table based on role retrieved
    if RoleName == 'tank':
      if NrOfTanksSignedUp == NrOfTanksRequired and NrOfTanksRequired > 0:
        await ReservesHelper.CheckReserves(bot, message, JoinedUserDisplayName, Description, LocalDate, Origin, UserID, RaidID, RoleName, RoleID)
        conn.close()
        return
      if NrOfTanksSignedUp < NrOfTanksRequired:
        try:
          c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp + 1, NrOfTanksSignedUp = NrOfTanksSignedUp + 1 WHERE ID = (?)", (RaidID,))
        except:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of signed up players and tanks")
          conn.close()
          return
    elif RoleName == 'dps':
      if NrOfDpsSignedUp == NrOfDpsRequired and NrOfDpsRequired > 0:
        await ReservesHelper.CheckReserves(bot, message, JoinedUserDisplayName, Description, LocalDate, Origin, UserID, RaidID, RoleName, RoleID)
        conn.close()
        return
      if NrOfDpsSignedUp < NrOfDpsRequired:
        try:
          c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp + 1, NrOfDpsSignedUp = NrOfDpsSignedUp + 1 WHERE ID = (?)", (RaidID,))
        except:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of signed up players and dps")
          conn.close()
          return
    elif RoleName == 'healer':
      if NrOfHealersSignedUp == NrOfHealersRequired and NrOfHealersRequired > 0:
        await ReservesHelper.CheckReserves(bot, message, JoinedUserDisplayName, Description, LocalDate, Origin, UserID, RaidID, RoleName, RoleID)
        conn.close()
        return
      if NrOfHealersSignedUp < NrOfHealersRequired:
        try:
          c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp + 1, NrOfHealersSignedUp = NrOfHealersSignedUp + 1 WHERE ID = (?)", (RaidID,))
        except:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of signed up players and healers")
          conn.close()
          return
    else:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to retrieve the role")
      conn.close()
      return

    try:
      c.execute("DELETE FROM RaidReserves where RaidID = (?) AND UserID = (?)", (RaidID, UserID,))
      c.execute("INSERT INTO RaidMembers (Origin, UserID, RaidID, RoleID) VALUES (?, ?, ?, ?)", (Origin, UserID, RaidID, RoleID))
      conn.commit()

      JoinedUserDisplayName = await UserHelper.GetDisplayName(message, UserID, bot)
      await message.channel.send(f"{JoinedUserDisplayName} has joined the party {Description} on {LocalDate} as a {RoleName}!")
      UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID)
      await message.edit(content=UpdatedMessage)
      await JoinHelper.NotifyOrganizer(message, bot, UserID, RaidID, Organizer, Description, LocalDate)
      conn.close()
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong joining you to this run.")
      conn.close()
	  return
