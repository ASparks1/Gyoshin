import sqlite3
import asyncio
from Helpers import OriginHelper
from Helpers import RoleHelper
from Helpers import UserHelper
from Helpers import DMHelper
from Helpers import DateTimeFormatHelper
from Helpers import RaidIDHelper
from Helpers import MessageHelper

async def WithdrawFromRaid(message, bot, UserID):
  try:
    RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)
  except ValueError:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong.")
    return

  # Get Origin
  Origin = await OriginHelper.GetOrigin(message)

  if not Origin:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving the server ID")
    return

  if not UserID:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving your user ID")
    return

  # Open connection to DB
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Execute query to see if user is already signed up to raid
  try:
    c.execute("SELECT R.ID as RaidID, R.Name, RM.ID as RaidMemberID, RM.UserID, RM.RoleID, R.Date, R.OrganizerUserID, R.NrOfPlayersSignedUp, R.NrOfTanksSignedUp, R.NrOfDpsSignedUp, R.NrOfHealersSignedUp FROM Raids R JOIN RaidMembers RM ON R.ID = RM.RaidID WHERE R.ID = (?) AND R.Origin = (?) AND RM.UserID = (?)", (RaidID, Origin, UserID,))
  except ValueError:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong checking if you're already signed up to this run")
    conn.close()
    return

  row = c.fetchone()

  if row:
    RaidID = row[0]
    RaidName = row[1]
    RaidMemberID = row[2]
    UserID = row[3]
    RoleID = row[4]
    Date = row[5]
    LocalDate = await DateTimeFormatHelper.SqliteToLocalNoCheck(Date)
    OrganizerID = row[6]
    UserName = await UserHelper.GetDisplayName(message, UserID, bot)

    if not UserName:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving the display name of a raid member")
      conn.close()
      return

    # Check if the user calling the command is also the organizer
    if OrganizerID == UserID:
      await DMHelper.DMUserByID(bot, UserID, "You cannot withdraw from this run because you're the organizer, please use the cancel button instead")
      conn.close()
      return

    # Get role name
    RoleName = await RoleHelper.GetRoleName(RoleID)

    # Update Raids table based on role retrieved
    if RoleName == 'tank':
      try:
        c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfTanksSignedUp = NrOfTanksSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
      except ValueError:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of signed up players and tanks")
        conn.close()
        return
    elif RoleName == 'dps':
      try:
        c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfDpsSignedUp = NrOfDpsSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
      except ValueError:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of signed up players and dps")
        conn.close()
        return
    elif RoleName == 'healer':
      try:
        c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfHealersSignedUp = NrOfHealersSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
      except ValueError:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of signed up players and healers")
        conn.close()
        return
    else:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to retrieve your role")
      conn.close()
      return

    # Delete RaidMembers child record
    try:
      c.execute("DELETE FROM RaidMembers WHERE ID = (?)", (RaidMemberID,))
      conn.commit()
    except ValueError:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to withdraw you from this run")
      conn.close()
      return

    # Check if there are still members signed up
    try:
      c.execute("SELECT UserID FROM RaidMembers WHERE RaidID = (?)", (RaidID,))
      rows = c.fetchall()

      # Delete the raid if there is nobody signed up anymore
      if not rows:

        c.execute("DELETE FROM Raids WHERE ID = (?)", (RaidID,))
        try:
          conn.commit()
          await message.channel.send(f"{UserName} has withdrawn from the run {RaidName} on {LocalDate} as you were the only person signed up for this the run has been cancelled")
          conn.close()
        except ValueError:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to withdraw you from this run")
          conn.close()
          return
      else:
        try:
          conn.commit()
          await message.channel.send(f"{UserName} has withdrawn from the run {RaidName} on {LocalDate}")
          UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID, Origin)
          await message.edit(content=UpdatedMessage)
          conn.close()
        except ValueError:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to withdraw you from this run")
          conn.close()
          return
    except ValueError:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to withdraw you from this run")
      conn.close()
      return

  else:
    await DMHelper.DMUser(message, "Unable to withdraw because you are not a member of this run")
    conn.close()
    return

  conn.close()
  return
