import sqlite3

# Helper function to change from tank to dps
async def TankToDPS(message, RaidID, NewRoleID, RaidMemberID, DisplayName, OldRoleName, RoleName, RaidName, LocalDate):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute("UPDATE Raids set NrOfTanksSignedUp = NrOfTanksSignedUp - 1, NrOfDpsSignedUp = NrOfDpsSignedUp + 1 WHERE ID = (?)", (RaidID,))
  c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?)", (NewRoleID, RaidMemberID,))
  await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
  conn.commit()
  conn.close()
  return

# Helper function to change from tank to healer
async def TankToHealer(message, RaidID, NewRoleID, RaidMemberID, DisplayName, OldRoleName, RoleName, RaidName, LocalDate):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute("UPDATE Raids set NrOfTanksSignedUp = NrOfTanksSignedUp - 1, NrOfHealersSignedUp = NrOfHealersSignedUp + 1 WHERE ID = (?)", (RaidID,))
  c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?)", (NewRoleID, RaidMemberID,))
  await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
  conn.commit()
  conn.close()
  return

# Helper function to change from dps to tank
async def DPSToTank(message, RaidID, NewRoleID, RaidMemberID, DisplayName, OldRoleName, RoleName, RaidName, LocalDate):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute("UPDATE Raids set NrOfDpsSignedUp = NrOfDpsSignedUp - 1, NrOfTanksSignedUp = NrOfTanksSignedUp + 1 WHERE ID = (?)", (RaidID,))
  c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?)", (NewRoleID, RaidMemberID,))
  await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
  conn.commit()
  conn.close()
  return

# Helper function to change from dps to healer
async def DPSToHealer(message, RaidID, NewRoleID, RaidMemberID, DisplayName, OldRoleName, RoleName, RaidName, LocalDate):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute("UPDATE Raids set NrOfDpsSignedUp = NrOfDpsSignedUp - 1, NrOfHealersSignedUp = NrOfHealersSignedUp + 1 WHERE ID = (?)", (RaidID,))
  c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?)", (NewRoleID, RaidMemberID,))
  await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
  conn.commit()
  conn.close()
  return

# Helper function to change from healer to tank
async def HealerToTank(message, RaidID, NewRoleID, RaidMemberID, DisplayName, OldRoleName, RoleName, RaidName, LocalDate):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute("UPDATE Raids set NrOfHealersSignedUp = NrOfHealersSignedUp - 1, NrOfTanksSignedUp = NrOfTanksSignedUp + 1 WHERE ID = (?)", (RaidID,))
  c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?)", (NewRoleID, RaidMemberID,))
  await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
  conn.commit()
  conn.close()
  return

# Helper function to change from healer to dps
async def HealerToDPS(message, RaidID, NewRoleID, RaidMemberID, DisplayName, OldRoleName, RoleName, RaidName, LocalDate):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute("UPDATE Raids set NrOfHealersSignedUp = NrOfHealersSignedUp - 1, NrOfDpsSignedUp = NrOfDpsSignedUp + 1 WHERE ID = (?)", (RaidID,))
  c.execute("UPDATE RaidMembers set RoleID = (?) WHERE ID = (?)", (NewRoleID, RaidMemberID,))
  await message.channel.send(f"{DisplayName} has changed role from {OldRoleName} to {RoleName} for {RaidName} on {LocalDate}")
  conn.commit()
  conn.close()
  return
