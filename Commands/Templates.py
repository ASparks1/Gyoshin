import sqlite3
from Helpers import OriginHelper
from Helpers import RoleIconHelper
from Helpers import DMHelper

async def GetTemplates(message, bot):
  # Get server ID
  Origin = await OriginHelper.GetOrigin(message)
  
  if not Origin:
    return

  # Open connection to the database
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Get role icons
  try:
    TankIcon = await RoleIconHelper.GetTankIcon(bot, 'Tank')
    DpsIcon = await RoleIconHelper.GetDpsIcon(bot, 'Dps')
    HealerIcon = await RoleIconHelper.GetHealerIcon(bot, 'Healer')
  except:
    await DMHelper.DMUser(message, f"Something went wrong retrieving role icons")
    return
  
  # Execute query
  try:
    c.execute(f"SELECT Name, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers FROM Templates WHERE Origin = (?)", (Origin,))
  except:
    await DMHelper.DMUser(message, f"Something went wrong trying to retrieve templates")
    conn.close()
    return

  # Store query results
  rows = c.fetchall()    

  if not rows:
    await DMHelper.DMUser(message, f"No templates found")
    conn.close()
    return
  
  # Start with an empty message
  Message = None    

  # Go through all rows found and post a message in channel for each one
  for row in rows:

    try:        
      Name = row[0]
      NrOfPlayers = row[1]
      NrOfTanks = row[2]
      NrOfDps = row[3]
      NrOfHealers = row[4]
    except:
      await DMHelper.DMUser(message, f"Unable to convert variables")
      conn.close()
      return
  
    if not Message:
        Message = f"The following templates are available on this server:\n"
        TemplateMessage = f"Name: {Name}\nNumber of players: {NrOfPlayers}\n{TankIcon} {NrOfTanks} {DpsIcon} {NrOfDps} {HealerIcon} {NrOfHealers}"
        Message = f"{Message}{TemplateMessage}\n"
    elif Message:
        TemplateMessage = f"Name: {Name}\nNumber of players: {NrOfPlayers}\n{TankIcon} {NrOfTanks} {DpsIcon} {NrOfDps} {HealerIcon} {NrOfHealers}"
        Message = f"{Message}{TemplateMessage}\n"
    
  await DMHelper.DMUser(message, f"{Message}")
    # Post message to channel
    # await DMHelper.DMUser(message, f"Name: {Name}\nNumber of players: {NrOfPlayers}\n{TankIcon} {NrOfTanks} {DpsIcon} {NrOfDps} {HealerIcon} {NrOfHealers}")
    # conn.close()

  # Close the connection to the database
  conn.close()
  return