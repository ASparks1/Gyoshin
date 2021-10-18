import sqlite3
from Helpers import OriginHelper
from Helpers import RoleIconHelper
from Helpers import DMHelper

async def GetTemplates(message):
  Origin = await OriginHelper.GetOrigin(message)

  if not Origin:
    return

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    TankIcon = await RoleIconHelper.GetTankIcon()
    DpsIcon = await RoleIconHelper.GetDpsIcon()
    HealerIcon = await RoleIconHelper.GetHealerIcon()
  except:
    await DMHelper.DMUser(message, "Something went wrong retrieving role icons")
    return

  try:
    c.execute("SELECT Name, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers FROM Templates WHERE Origin = (?)", (Origin,))
  except:
    await DMHelper.DMUser(message, "Something went wrong trying to retrieve templates")
    conn.close()
    return

  rows = c.fetchall()

  if not rows:
    await DMHelper.DMUser(message, "No templates found")
    conn.close()
    return

  Message = None
  for row in rows:
    try:
      Name = row[0]
      NrOfPlayers = row[1]
      NrOfTanks = row[2]
      NrOfDps = row[3]
      NrOfHealers = row[4]
    except:
      await DMHelper.DMUser(message, "Unable to convert variables")
      conn.close()
      return

    if not Message:
        Message = "The following templates are available on this server:\n"
        TemplateMessage = f"Name: {Name}\nNumber of players: {NrOfPlayers}\n{TankIcon} {NrOfTanks} {DpsIcon} {NrOfDps} {HealerIcon} {NrOfHealers}"
        Message = f"{Message}{TemplateMessage}\n"
    elif Message:
        TemplateMessage = f"Name: {Name}\nNumber of players: {NrOfPlayers}\n{TankIcon} {NrOfTanks} {DpsIcon} {NrOfDps} {HealerIcon} {NrOfHealers}"
        Message = f"{Message}{TemplateMessage}\n"

  await DMHelper.DMUser(message, f"{Message}")
  conn.close()
  return
