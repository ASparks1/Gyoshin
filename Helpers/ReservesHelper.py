import sqlite3
import discord
from Helpers import DMHelper

# Helper function to join reserves
async def JoinReserves(bot, message, JoinedUserDisplayName, Description, LocalDate, Origin, UserID, RaidID, RoleID, RoleName):
  try:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()
	
    c.execute(f"INSERT INTO RaidReserves (Origin, UserID, RaidID, RoleID) VALUES (?, ?, ?, ?)", (Origin, UserID, RaidID, RoleID))
    conn.commit()
    await message.channel.send(f"{JoinedUserDisplayName} has joined the party {Description} on {LocalDate} as a reserve {RoleName}!")
    return
  except:
    await DMHelper.DMUserByID(bot, UserID, f"Something went wrong adding you to the reserves")
    conn.close()
    return

# Helper function to withdraw from reserves
async def WithdrawFromReserves(bot, message, JoinedUserDisplayName, Description, LocalDate, Origin, UserID, RaidID):
  try:
    conn = sqlite3.connect('RaidPlanner.db')
    c = conn.cursor()
	
    c.execute(f"DELETE FROM RaidReserves WHERE Origin = (?) AND RaidID = (?) and UserID = (?)", (Origin, RaidID, UserID,))
    conn.commit()
    await message.channel.send(f"{JoinedUserDisplayName} has withdrawn from the reserves for the party {Description} on {LocalDate}!")
    return
  except:
    await DMHelper.DMUserByID(bot, UserID, f"Something went wrong removing you from the reserves")
    conn.close()
    return