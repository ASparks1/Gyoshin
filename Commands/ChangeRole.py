import re
import sqlite3
from Helpers import RoleHelper
from Helpers import DateTimeFormatHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import DMHelper
from Helpers import RaidIDHelper
from Helpers import MessageHelper

async def ChangeRole(message, bot, RoleName, UserID):
  try:
    RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining run information")
    return

  # Get discord server ID
  Origin = await OriginHelper.GetOrigin(message)

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Check if the run exists and if the user is a member
  try:
    c.execute("SELECT RM.RoleID, RM.ID, R.ID, R.NrOfTanksRequired, R.NrOfTanksSignedUp, R.NrOfDpsRequired, R.NrOfDpsSignedUp, R.NrOfHealersRequired, R.NrOfHealersSignedUp, R.Name, R.Date FROM RaidMembers RM JOIN Raids R ON R.ID = RM.RaidID WHERE RM.Origin = (?) AND R.ID = (?) AND RM.UserID = (?)", (Origin, RaidID, UserID,))
    row = c.fetchone()

    OldRoleID = row[0]
    RaidMemberID = row[1]
    RaidID = row[2]
    NrOfTanksRequired = row[3]
    NrOfTanksSignedUp = row[4]
    NrOfDpsRequired = row[5]
    NrOfDpsSignedUp = row[6]
    NrOfHealersRequired = row[7]
    NrOfHealersSignedUp = row[8]
    RaidName = row[9]
    Date = row[10]
    Date = await DateTimeFormatHelper.SqliteToLocal(message, Date)
    OldRoleName = await RoleHelper.GetRoleName(OldRoleID)
    NewRoleID = await RoleHelper.GetRoleID(RoleName)    
    DisplayName = await UserHelper.GetDisplayName(message, UserID, bot)
    conn.close()
    return

    if (OldRoleID != NewRoleID):
      # Create an empty message variable first
      UpdatedMessage = None
      # Change from tank to dps
      if OldRoleName == 'tank' and RoleName == 'dps' and NrOfDpsSignedUp < NrOfDpsRequired:
        c.execute("UPDATE Raids set NrOfTanksSignedUp = NrOfTanksSignedUp - 1, NrOfDpsSignedUp = NrOfDpsSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?) AND Origin = (?)", (NewRoleID, RaidMemberID, Origin,))
        await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
        conn.commit()
        UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID, Origin)

      # Change from tank to healer
      elif OldRoleName == 'tank' and RoleName == 'healer' and NrOfHealersSignedUp < NrOfHealersRequired:
        c.execute("UPDATE Raids set NrOfTanksSignedUp = NrOfTanksSignedUp - 1, NrOfHealersSignedUp = NrOfHealersSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?) AND Origin = (?)", (NewRoleID, RaidMemberID, Origin,))
        await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
        conn.commit()
        UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID, Origin)

      # Change from dps to tank
      elif OldRoleName == 'dps' and RoleName == 'tank' and NrOfTanksSignedUp < NrOfTanksRequired:
        c.execute("UPDATE Raids set NrOfDpsSignedUp = NrOfDpsSignedUp - 1, NrOfTanksSignedUp = NrOfTanksSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?) AND Origin = (?)", (NewRoleID, RaidMemberID, Origin,))
        await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
        conn.commit()
        UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID, Origin)

      # Change from dps to healer
      elif OldRoleName == 'dps' and RoleName == 'healer' and NrOfHealersSignedUp < NrOfHealersRequired:
        c.execute("UPDATE Raids set NrOfDpsSignedUp = NrOfDpsSignedUp - 1, NrOfHealersSignedUp = NrOfHealersSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?) AND Origin = (?)", (NewRoleID, RaidMemberID, Origin,))
        await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
        conn.commit()
        UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID, Origin)
        
      # Change from healer to tank
      elif OldRoleName == 'healer' and RoleName == 'tank' and NrOfTanksSignedUp < NrOfTanksRequired:
        c.execute("UPDATE Raids set NrOfHealersSignedUp = NrOfHealersSignedUp - 1, NrOfTanksSignedUp = NrOfTanksSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?) AND Origin = (?)", (NewRoleID, RaidMemberID, Origin,))
        await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
        conn.commit()
        UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID, Origin)

      # Change from healer to dps
      elif OldRoleName == 'healer' and RoleName == 'dps' and NrOfDpsSignedUp < NrOfDpsRequired:
        c.execute("UPDATE Raids set NrOfHealersSignedUp = NrOfHealersSignedUp - 1, NrOfDpsSignedUp = NrOfDpsSignedUp + 1 WHERE ID = (?) AND Origin = (?)", (RaidID, Origin,))
        c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?) AND Origin = (?)", (NewRoleID, RaidMemberID, Origin,))
        await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
        conn.commit()
        UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID, Origin)
      
      try:
        if UpdatedMessage:
          await message.edit(content=UpdatedMessage)
          conn.close()
          return
        if not UpdatedMessage:
          await DMHelper.DMUserByID(bot, UserID, f"Something went wrong changing your role, please make sure you're changing to a role that still has free slots")
          conn.close()
          return
      except:
        await DMHelper.DMUserByID(bot, UserID, f"Something went wrong changing your role")
        conn.close()
        return
    else:
      await DMHelper.DMUserByID(bot, UserID, f"You cannot change to the same role you already signed up as")
      conn.close()
      return
  except:
        await DMHelper.DMUserByID(bot, UserID, f"Something went wrong changing your role")
        conn.close()
        return
