import sqlite3
from Helpers import DMHelper
from Helpers import OriginHelper

async def ListRoles(message):
  Origin = await OriginHelper.GetOrigin(message)
  if not Origin:
    return

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    c.execute("SELECT Name FROM Roles ORDER BY Name ASC")
  except:
    await DMHelper.DMUser(message, "Something went wrong trying to retrieve roles")
    conn.close()
    return

  rows = c.fetchall()
  if not rows:
    await DMHelper.DMUser(message, "No roles found")
    conn.close()
    return

  Message = None
  for row in rows:
    try:
      Name = row[0]
      RolesMessage = (f"{Name}")
      if not Message:
        Message = f"The following roles are available:\n{RolesMessage}"
      elif Message:
        Message = f"{Message}\n{RolesMessage}"
    except:
      await DMHelper.DMUser(message, "Unable to assign variables")
      conn.close()
      return
  await DMHelper.DMUser(message, f"{Message}")
  conn.close()
  return
