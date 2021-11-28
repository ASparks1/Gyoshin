import sqlite3
from Helpers import RoleHelper
from Helpers import DMHelper

async def DismissMember(bot, RaidID, MemberID, UserID):
  if RaidID and MemberID:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()
    try:
      c.execute("SELECT ID, RoleID FROM RaidMembers WHERE RaidID = (?) AND UserID = (?)", (RaidID, MemberID))
      row = c.fetchone()
      if row:
        RaidMemberID = row[0]
        RoleID = row[1]
        RoleName = await RoleHelper.GetRoleName(RoleID)
        c.execute("DELETE FROM RaidMembers WHERE ID = (?)", (RaidMemberID,))
      else:
        conn.close()
        return

      if RoleName == 'tank':
        c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfTanksSignedUp = NrOfTanksSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
      elif RoleName == 'dps':
        c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfDpsSignedUp = NrOfDpsSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
      elif RoleName == 'healer':
        c.execute("Update Raids SET NrOfPlayersSignedUp = NrOfPlayersSignedUp - 1, NrOfHealersSignedUp = NrOfHealersSignedUp - 1, Status = 'Forming' WHERE ID = (?)", (RaidID,))
      conn.commit()
      conn.close()
      return
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of signed up players")
      conn.close()
      return
