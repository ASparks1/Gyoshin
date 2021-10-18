import sqlite3

async def GetRoleName(RoleID):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  try:
    c.execute("SELECT Name FROM Roles WHERE ID = (?)", (RoleID,))
    RoleName = c.fetchone()[0]
  except:
    conn.close()
  return RoleName

async def GetRoleID(RoleName):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  try:
    c.execute("SELECT ID FROM Roles WHERE Name = (?)", (RoleName,))
    RoleID = c.fetchone()[0]
  except:
    conn.close()
  return RoleID
