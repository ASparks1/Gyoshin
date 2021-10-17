import sqlite3
import discord
from Helpers import DMHelper
from Helpers import RoleHelper
from Helpers import RoleIconHelper
from Helpers import UserHelper
from Helpers import NotificationHelper

# Helper function to clean up a users' data when they get kicked from or leave the server
async def OnMemberLeaveOrRemove(member):
  try:
    UserID = member.id
    Origin = member.guild.id
    print("User {UserID} has left the server {Origin}, checking if they have data that needs to be cleaned up now!")

    # Open database connection
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()

    # Delete all raids where this user is the organizer
    c.execute("SELECT ID FROM Raids WHERE UserOrganizerID = (?) AND Origin = (?)", (UserID, Origin,))
    rows = c.fetchall()

    if rows:
      RaidID = rows[0]
      c.execute("DELETE FROM Raids WHERE RaidID = (?)", (RaidID,))
      c.execute("DELETE FROM RaidReserves WHERE RaidID = (?)", (RaidID,))
      conn.commit()

    # Find all the runs this user has signed up for and is not the organizer
    c.execute("Select R.ID, R.Status, R.NrOfPlayersSignedUp, RM.ID, RM.RoleID FROM Raids R JOIN RaidMembers RM ON R.ID = RM.RaidID WHERE OrganizerUserID != (?) AND UserID = (?) AND Origin = (?)", (UserID, UserID, Origin,))
    rows = c.fetchall()

    if rows:
      print(f"Cleaning up raid data for user {UserID} on server {Origin}")
      for row in rows:
        RaidID = row[0]
        Status = row[1]
        NrOfPlayersSignedUp = row[2]
        RaidMemberID = row[3]
        RoleID = row[4]

	    # Delete run if the status is canceled or the number of players signed up is just 1
        if NrOfPlayersSignedUp == 1:
          c.execute("DELETE FROM Raids WHERE ID = (?)", (RaidID,))
        if Status == "Cancelled":
          c.execute("DELETE FROM Raids WHERE ID = (?)", (RaidID,))
        elif Status == "Formed" or "Forming":
          # First obtain the role this user was signed up as
          RoleName = await RoleHelper.GetRoleName(RoleID)
          # Set the column name to be updated according to the role
          if RoleName == "tank":
            c.execute("UPDATE Raids SET NrOfTanksSignedUp = NrOfTanksSignedUp - 1, NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
          elif RoleName == "dps":
            c.execute("UPDATE Raids SET NrOfDpsSignedUp = NrOfDpsSignedUp - 1, NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
          elif RoleName == "healer":
            c.execute("UPDATE Raids SET NrOfHealersSignedUp = NrOfHealersSignedUp - 1, NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
          # Delete raidmember record first
          c.execute("DELETE FROM RaidMembers WHERE ID = (?)", (RaidMemberID,))
          # Update run with new information

      # Commit changes and close the connection
      conn.commit()
      conn.close()
    else:
      print(f"No data found to clean up for user {UserID}")
      conn.close()

  except:
    print("Something went wrong deleting old data")
    return

# Helper function to list raid members or reserves
async def ListMembers(bot, message, Type, RaidID):
  # Start with an empty message
  Message = None
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  if Type == 'Members':
    c.execute("SELECT UserID, RoleID FROM RaidMembers WHERE RaidID = (?) ORDER BY RoleID", (RaidID,))
    rows = c.fetchall()
  elif Type == 'Reserves':
    c.execute("SELECT UserID, RoleID FROM RaidReserves WHERE RaidID = (?) ORDER BY RoleID", (RaidID,))
    rows = c.fetchall()

  for row in rows:
    try:
      UserID = row[0]
      RoleID = row[1]
      RoleName = await RoleHelper.GetRoleName(RoleID)
      UserName = await UserHelper.GetDisplayName(message, UserID, bot)
      if not RoleName:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving the role name for one of the members")
        conn.close()
        return

      if not UserName:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving the display name for one of the members, perhaps they have left the server")
        conn.close()

      if RoleName == 'tank':
        RoleIcon = await RoleIconHelper.GetTankIcon()
      elif RoleName == 'dps':
        RoleIcon = await RoleIconHelper.GetDpsIcon()
      elif RoleName == 'healer':
        RoleIcon = await RoleIconHelper.GetHealerIcon()

      if not Message:
        MemberRoleMessage = f"{RoleIcon} - {UserName}\n"
        Message = f"{MemberRoleMessage}"
      elif Message:
        MemberRoleMessage = f"{RoleIcon} - {UserName}\n"
        Message = f"{Message}{MemberRoleMessage}"
    except:
      await DMHelper.DMUserByID(bot, UserID, "Unable to convert variables")
      conn.close()
      return
  conn.close()
  return Message

# Helper function to check if there are members signed up besides the organizer and generate notifications (used in cancel and reschedule functionality)
async def CheckForMembersBesidesOrganizer(bot, message, RaidID, UserID):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    c.execute("SELECT UserID FROM RaidMembers WHERE RaidID = (?) AND UserID != (?)", (RaidID, UserID,))
    UserIDs = c.fetchall()
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving raid members memberhelper1")
    conn.close()
    return

  try:
    if not UserIDs:
      conn.close()
      return

    if UserIDs:
      c.execute("SELECT UserID FROM RaidMembers WHERE RaidID = (?) AND UserID != (?)", (RaidID, UserID,))
      RaidMembers = c.fetchall()

    if RaidMembers:
      MemberNotifications = await NotificationHelper.NotifyRaidMembers(message, RaidMembers)
      conn.close()
      return MemberNotifications
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving raidmembers memberhelper2")
    conn.close()
    return
