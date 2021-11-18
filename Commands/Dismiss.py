import sqlite3
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleHelper
from Helpers import DMHelper

async def DismissMember(message, client):
  commands = message.content.split()
  try:
    RaidID = commands[1]
    UserID = message.mentions[0].id
  except:
    await DMHelper.DMUser(message, "Something went wrong processing the run number or user to dismiss")
    return

  UserName = await UserHelper.GetDisplayName(message, UserID, client)
  Creator = message.author.id

  if not Creator:
    await DMHelper.DMUser(message, "Something went wrong retrieving the user ID")
    # Delete message that contains command
    await message.delete()
    return

  if UserID == Creator:
        await DMHelper.DMUser(message, "You cannot dismiss yourself as the organizer of this run")
        await message.delete()
        return

  await message.delete()

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    c.execute("SELECT ID, Name, Date FROM Raids WHERE ID = (?)", (RaidID,))
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
    try:
      c.execute("SELECT ID, RoleID FROM RaidMembers WHERE RaidID = (?) AND UserID = (?)", (RaidID, UserID,))
      row = c.fetchone()
      RaidMemberID = row[0]
      RoleID = row[1]
      RoleName = await RoleHelper.GetRoleName(RoleID)
    except:
      await DMHelper.DMUser(message, "Something went wrong checking if the provided member is part of this run")
      conn.close()
      return
  else:
    conn.close()
    return

  if RaidMemberID:
    try:
      c.execute("DELETE FROM RaidMembers WHERE ID = (?)", (RaidMemberID,))
    except:
      await DMHelper.DMUser(message, "Something went wrong removing this member from the run")
      conn.close()
      return

    try:
      if RoleName == 'tank':
        c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfTanksSignedUp = NrOfTanksSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
      elif RoleName == 'dps':
        c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfDpsSignedUp = NrOfDpsSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
      elif RoleName == 'healer':
        c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfHealersSignedUp = NrOfHealersSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
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
  else:
    conn.close()
    return
