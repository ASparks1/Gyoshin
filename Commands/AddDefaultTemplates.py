import sqlite3
from Helpers import OriginHelper
from Helpers import DMHelper

async def AddDefaultTemplates(message):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    Origin = await OriginHelper.GetOrigin(message)
    if not Origin:
      return

    CreatorID = message.author.id
    c.execute("INSERT INTO Templates (Name, Origin, CreatorUserID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES ('alliance', (?), (?), 24, 3, 15, 6)", (Origin, CreatorID,))
    c.execute("INSERT INTO Templates (Name, Origin, CreatorUserID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES ('raid', (?), (?), 8, 2, 4, 2)", (Origin, CreatorID,))
    c.execute("INSERT INTO Templates (Name, Origin, CreatorUserID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES ('dungeon', (?), (?), 4, 1, 2, 1)", (Origin, CreatorID,))
    c.execute("INSERT INTO Templates (Name, Origin, CreatorUserID, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES ('maps', (?), (?), 8, 1, 6, 1)", (Origin, CreatorID,))
    conn.commit()
    await DMHelper.DMUser(message, "Default templates added")
    conn.close()
  except:
    await DMHelper.DMUser(message, "Something went wrong trying to insert default templates")
    conn.close()
