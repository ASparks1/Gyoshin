import sqlite3
import discord
from Helpers import RoleHelper

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
      c.execute("DELETE FROM Raids WHERE RaidID = (?) AND Origin = (?)", (RaidID, Origin,))
      c.execute("DELETE FROM RaidReserves WHERE RaidID = (?)", (RaidID,))
      conn.commit()

    # Find all the runs this user has signed up for and is not the organizer
    c.execute("Select R.ID, R.Status, R.NrOfPlayersSignedUp, R.NrOfTanksSignedUp, R.NrOfDpsSignedUp, R.NrOfHealersSignedUp, RM.ID, RM.RoleID FROM Raids R JOIN RaidMembers RM ON R.ID = RM.RaidID WHERE OrganizerUserID != (?) AND UserID = (?) AND Origin = (?)", (UserID, UserID, Origin,))
    rows = c.fetchall()

    if rows:
      print(f"Cleaning up raid data for user {UserID} on server {Origin}")
      for row in rows:
        RaidID = row[0]
        Status = row[1]
        NrOfPlayersSignedUp = row[2]
        NrOfTanksSignedUp = row[3]
        NrOfDpsSignedUp = row[4]
        NrOfHealersSignedUp = row[5]
        RaidMemberID = row[6]
        RoleID = row[7]

	    # Delete run if the status is canceled or the number of players signed up is just 1
        if NrOfPlayersSignedUp == 1:
          c.execute("DELETE FROM Raids WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        if Status == "Cancelled":
          c.execute("DELETE FROM Raids WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        elif Status == "Formed" or "Forming":
          # First obtain the role this user was signed up as
          RoleName = await RoleHelper.GetRoleName(RoleID)
          # Set the column name to be updated according to the role
          if RoleName == "tank":
            ColumnToUpdate = 'NrOfTanksSignedUp'
          elif RoleName == "dps":
            ColumnToUpdate = 'NrOfDpsSignedUp'
          elif RoleName == "healer":
            ColumnToUpdate = 'NrOfHealersSignedUp'
          # Delete raidmember record first
          c.execute("DELETE FROM RaidMembers WHERE ID = (?) AND Origin = (?)", (RaidMemberID, Origin,))
          # Update run with new information
          c.execute("UPDATE Raids SET (?) = (?) - 1, NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, Status = 'Forming' WHERE ID = (?) AND Origin = (?)", (ColumnToUpdate, ColumnToUpdate, RaidID, Origin,))

      # Commit changes and close the connection
      conn.commit()
      conn.close()
    else:
      print(f"No data found to clean up for user {UserID}")
      conn.close()
 
  except:
    print("Something went wrong deleting old data")
    return
