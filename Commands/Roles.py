import sqlite3
from Helpers import DMHelper
from Helpers import OriginHelper

async def ListRoles(message):

  # Get server ID
  Origin = await OriginHelper.GetOrigin(message)
  
  if not Origin:
    return

  # Open connection to the database
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()  
    
  # Execute query
  try:
    c.execute("SELECT Name FROM Roles ORDER BY Name ASC")
  except:
    await DMHelper.DMUser(message, "Something went wrong trying to retrieve roles")
    conn.close()
    return

  # Store query results
  rows = c.fetchall()

  if not rows:
    await DMHelper.DMUser(message, "No roles found")
    conn.close()
    return
  
  # Start with an empty message
  Message = None
  
  # Go through all rows found and post a message in channel for each one
  for row in rows:

    # Data type conversion so values can be used in message
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