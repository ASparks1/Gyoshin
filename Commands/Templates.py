import sqlite3
from Helpers import OriginHelper
from Helpers import RoleIconHelper
from Helpers import DMHelper

async def GetTemplates(ctx, bot):
  UserID = ctx.author.id
  Origin = await OriginHelper.GetOrigin(ctx, bot, UserID)
  if not Origin:
    return

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    TankIcon = await RoleIconHelper.GetTankIcon()
    DpsIcon = await RoleIconHelper.GetDpsIcon()
    HealerIcon = await RoleIconHelper.GetHealerIcon()
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving role icons")
    return

  try:
    c.execute("SELECT Name, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers FROM Templates WHERE Origin = (?)", (Origin,))
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to retrieve templates")
    conn.close()
    return

  rows = c.fetchall()
  if not rows:
    await DMHelper.DMUserByID(bot, UserID, "No templates found")
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
      await DMHelper.DMUserByID(bot, UserID, "Unable to convert variables")
      conn.close()
      return

    if not Message:
        Message = "The following templates are available on this server:\n"
        TemplateMessage = f"Name: {Name}\nNumber of players: {NrOfPlayers}\n{TankIcon} {NrOfTanks} {DpsIcon} {NrOfDps} {HealerIcon} {NrOfHealers}"
        Message = f"{Message}{TemplateMessage}\n"
    elif Message:
        TemplateMessage = f"Name: {Name}\nNumber of players: {NrOfPlayers}\n{TankIcon} {NrOfTanks} {DpsIcon} {NrOfDps} {HealerIcon} {NrOfHealers}"
        Message = f"{Message}{TemplateMessage}\n"

  await DMHelper.DMUserByID(bot, UserID, f"{Message}")
  conn.close()
  return
