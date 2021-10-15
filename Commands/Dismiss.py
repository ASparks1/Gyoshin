import sqlite3
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleHelper
from Helpers import DMHelper

async def DismissMember(message, client):

  commands = message.content.split()

  # Get Index values for commands
  try:
    RaidID = commands[1]
    UserID = message.mentions[0].id
  except ValueError:
    await DMHelper.DMUser(message, "Something went wrong processing the run number or user to dismiss")
    return

  # Get display name of user on the server
  UserName = await UserHelper.GetDisplayName(message, UserID, client)

  # Get Discord server id
  Origin = await OriginHelper.GetOrigin(message)

  if not Origin:
    await DMHelper.DMUser(message, "An error occurred trying to resolve the server ID")
    # Delete message that contains command
    await message.delete()
    return

  # Get user ID of the person who entered the commands
  Creator = message.author.id

  if not Creator:
    await DMHelper.DMUser(message, "Something went wrong retrieving the user ID")
    # Delete message that contains command
    await message.delete()
    return

  if UserID == Creator:
        await DMHelper.DMUser(message, "You cannot dismiss yourself as the organizer of this run")
        # Delete message that contains command
        await message.delete()
        return

  # Delete message that contains the command
  await message.delete()

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Search if raid exists and check if the user who entered the command is the organizer
  try:
    c.execute("SELECT ID, Name, Date FROM Raids WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
    row = c.fetchone()
    RaidID = row[0]
    RaidName = row[1]
    Date = row[2]
    Date = await DateTimeFormatHelper.SqliteToLocal(message, Date)
  except:
    await DMHelper.DMUser(message, f"Run {RaidID} not found or you are not the organizer of this run, only the organizer is allowed to dismiss members.")
    conn.close()
    return

  if RaidID:
    # Check if the user is part of this run
    try:
      c.execute("SELECT ID, RoleID FROM RaidMembers WHERE RaidID = (?) AND Origin = (?) AND UserID = (?)", (RaidID, Origin, UserID,))
      row = c.fetchone()
      RaidMemberID = row[0]
      RoleID = row[1]
      RoleName = await RoleHelper.GetRoleName(RoleID)
    except:
      await DMHelper.DMUser(message, "Something went wrong checking if the provided member is part of this run")
      conn.close()
      return

  if RaidMemberID:
    try:
      c.execute("DELETE FROM RaidMembers WHERE ID = (?) AND Origin = (?)", (RaidMemberID, Origin,))
    except:
      await DMHelper.DMUser(message, "Something went wrong removing this member from the run")
      conn.close()
      return

    # Update Raids table based on role retrieved
    if RoleName == 'tank':
      ColumnToUpdate = 'NrOfTanksSignedUp'
    elif RoleName == 'dps':
      ColumnToUpdate = 'NrOfDpsSignedUp'
    elif RoleName == 'healer':
      ColumnToUpdate = 'NrOfHealersSignedUp'

    try:
      c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, (?) = (?) - 1, Status = 'Forming' WHERE ID = (?)", (ColumnToUpdate, RaidID,))
    except:
      await DMHelper.DMUser(message, "Something went wrong updating the number of signed up players")
      conn.close()
      return
    try:
      conn.commit()
      await message.channel.send(f"{UserName} has been dismissed from the run {RaidName} on {Date}")
      conn.close()
    except:
      conn.close()
      await DMHelper.DMUser(message, "Something went wrong dismissing a member from this run")
      return
