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
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving the run number.")
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
    c.execute("SELECT ID, Name, Date, Origin, OrganizerUserID, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfHealersSignedUp, Status FROM Raids WHERE ID = (?)", (RaidID,))
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
    NrOfTanksRequired = row[5]
    NrOfTanksSignedUp = row[6]
    NrOfDpsRequired = row[7]
    NrOfDpsSignedUp = row[8]
    NrOfHealersRequired = row[9]
    NrOfHealersSignedUp = row[10]
    Status = row[11]
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
      await JoinHelper.WithdrawHelper(message, bot, UserID, Description, LocalDate, GuildName, RoleNameSignedUpAs)
      conn.close()
    # Offer to change role if user is signed up with another role
    elif RoleID != RoleIDSignedUpAs:
      await JoinHelper.ChangeRoleHelper(message, bot, UserID, Description, LocalDate, GuildName, RoleNameSignedUpAs, RoleName)
      conn.close()

  if not usercheck:
    JoinedUserDisplayName = await UserHelper.GetDisplayName(message, UserID, bot)
    # Update Raids table based on role retrieved
    if RoleName == 'tank':
      await JoinHelper.JoinTank(bot, message, UserID, NrOfTanksSignedUp, NrOfTanksRequired, JoinedUserDisplayName, Description, LocalDate, Origin, RaidID, RoleName, RoleID, Organizer)
      conn.close()
    elif RoleName == 'dps':
      await JoinHelper.JoinDPS(bot, message, UserID, NrOfDpsSignedUp, NrOfDpsRequired, JoinedUserDisplayName, Description, LocalDate, Origin, RaidID, RoleName, RoleID, Organizer)
      conn.close()
    elif RoleName == 'healer':
      await JoinHelper.JoinHealer(bot, message, UserID, NrOfHealersSignedUp, NrOfHealersRequired, JoinedUserDisplayName, Description, LocalDate, Origin, RaidID, RoleName, RoleID, Organizer)
      conn.close()
    else:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to retrieve the role")
      conn.close()
      return
