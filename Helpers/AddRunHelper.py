import asyncio
import re
import sqlite3
from discord import ChannelType
from discord_components import DiscordComponents, Button, ButtonStyle
from Helpers import DateTimeFormatHelper
from Helpers import DMHelper
from Helpers import RoleHelper
from Helpers import RoleIconHelper

# Helper function to get users' run name input
async def GetRunName(bot, message, UserID, CreatorDisplay, GuildName):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  await DMHelper.DMUserByID(bot, UserID, f"Hi {CreatorDisplay}, let's get you forming your crew in {GuildName}.\nFirst, give me a brief description for your crew, e.g. 'Friday Night Alliance Raid'.\n")
  try:
    response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
    Name = response.content
    return Name
  except asyncio.TimeoutError:
    await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
    return

# Helper function to get users' date time input
async def GetRunDateTime(bot, message, UserID):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  DateTime = None
  while not DateTime:
    try:
      await DMHelper.DMUserByID(bot, UserID, "Now, please tell me the date and time of your run in the format of 'dd-mm-yyyy hh:mm'.")
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
      return

    pattern = re.compile(r'((\d{2})-(\d{2})-(\d{4})) (\d{2}):(\d{2})')
    match = pattern.match(response.content)
    if not match:
      await DMHelper.DMUserByID(bot, UserID, "Invalid date and time detected, please use the dd-mm-yyyy hh:mm format")
      continue

    try:
      sqldatetime = await DateTimeFormatHelper.LocalToSqlite(message, response.content)
      if not sqldatetime:
        await DMHelper.DMUserByID(bot, UserID, "Invalid date and time detected, please use the dd-mm-yyyy hh:mm format")
        continue
    except:
      await DMHelper.DMUserByID(bot, UserID, "Invalid date and time detected, please use the dd-mm-yyyy hh:mm format")
      continue

    try:
      DateTime = response.content
      return DateTime
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong saving the date & time")
      return

# Helper function to ask if user wants to use a template
async def UseTemplateQuestion(bot, message, UserID, Origin):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  UsingTemplate = None
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()
  c.execute("SELECT ID FROM Templates WHERE Origin = (?)", (Origin,))
  row = c.fetchone()
  if row:
    while not UsingTemplate:
      try:
        await DMHelper.DMUserByID(bot, UserID, "Do you wish to use a template (Y/N)?")
        response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      except asyncio.TimeoutError:
        await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
        conn.close()
        return

      if response.content in("Y","y","Yes","yes"):
        UsingTemplate = "yes"
        conn.close()
        return UsingTemplate
      if response.content in("N","n","No","no"):
        UsingTemplate = "no"
        conn.close()
        return UsingTemplate
      if response.content not in("N","n","No","no","Y","y","Yes","yes"):
        await DMHelper.DMUserByID(bot, UserID, "Please enter a valid response of 'yes' or 'no'.")
  else:
    UsingTemplate = "no"
    conn.close()
    return UsingTemplate

# Helper function for using a template
async def UseTemplateToCreateRun(bot, message, UserID, Origin, CreatorDisplay, ChannelID, Name, DateTime, sqldatetime):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  Template = None
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  while not Template:
    try:
      await DMHelper.DMUserByID(bot, UserID, "Which template would you like to use from the list above? Please respond with the name of the template.")
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
      conn.close()
      return

    Template = response.content
    try:
      c.execute("SELECT NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers FROM Templates WHERE Name = (?) and Origin = (?)", (Template, Origin))
      row = c.fetchone()
      if not row:
        await DMHelper.DMUserByID(bot, UserID, f"I could not find the template {Template} on this server, please ensure name is correct.")
        continue
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong checking for template, please try again.")
      continue

    try:
      NrOfPlayers = row[0]
      NrOfTanks = row[1]
      NrOfDps = row[2]
      NrOfHealers = row[3]
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining the player and/or role numbers from the template, please try again.")
      continue

  RoleID = await GetOrganizerRoleID(bot, message, UserID, NrOfTanks, NrOfDps, NrOfHealers)
  print(RoleID)
  if RoleID == 1:
    NumberOfCurrentTanks = 1
    NumberOfCurrentDps = 0
    NumberOfCurrentHealers = 0
  elif RoleID == 2:
    NumberOfCurrentDps = 1
    NumberOfCurrentTanks = 0
    NumberOfCurrentHealers = 0
  elif RoleID == 3:
    NumberOfCurrentHealers = 1
    NumberOfCurrentTanks = 0
    NumberOfCurrentDps = 0

  Status = await GetRunStatusToSet(NrOfPlayers)
  Confirm = await SummarizeRunInfoForConfirmation(bot, message, UserID, Name, DateTime, NrOfTanks, NrOfHealers, NrOfDps)

  if Confirm == "yes":
    await CreateRun(bot, message, UserID, Name, Origin, sqldatetime, NrOfPlayers, NrOfTanks, NumberOfCurrentTanks, NrOfDps, NumberOfCurrentDps, NrOfHealers, NumberOfCurrentHealers, Status, ChannelID, RoleID, CreatorDisplay, DateTime)
  if Confirm == "no":
    await DMHelper.DMUserByID(bot, UserID, "Your request to create a crew has been cancelled, please call the command again in the relevant channel if you wish to try again.")

# Helper function to get number of players
async def GetNrOfPlayers(bot, message, UserID):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  NrOfPlayers = None
  while not NrOfPlayers:
    try:
      await DMHelper.DMUserByID(bot, UserID, "What is the total number of players for your crew? Please enter a number greater than 0.")
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      try:
        NrOfPlayers = int(response.content)
        if NrOfPlayers <= 0:
          NrOfPlayers = None
          await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number greater than 0.")
          continue
      except:
        await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
        continue
      return NrOfPlayers
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
      return

# Helper function to get number of tanks
async def GetNrOfTanks(bot, message, UserID):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  NrOfTanks = None
  while not NrOfTanks:
    try:
      await DMHelper.DMUserByID(bot, UserID, "What is the total number of tanks for your crew? Please enter a number greater than 0.")
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      try:
        NrOfTanks = int(response.content)
        if NrOfTanks <= 0:
          NrOfTanks = None
          await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number greater than 0.")
          continue
      except:
        await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
        continue
      return NrOfTanks
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
      return

# Helper function to get number of dps
async def GetNrOfDPS(bot, message, UserID):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  NrOfDPS = None
  while not NrOfDPS:
    try:
      await DMHelper.DMUserByID(bot, UserID, "What is the total number of dps for your crew? Please enter a number greater than 0.")
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      try:
        NrOfDPS = int(response.content)
        if NrOfDPS <= 0:
          NrOfDPS = None
          await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number greater than 0.")
          continue
      except:
        await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
        continue
      return NrOfDPS
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
      return

# Helper function to get number of healers
async def GetNrOfHealers(bot, message, UserID):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  NrOfHealers = None
  while not NrOfHealers:
    try:
      await DMHelper.DMUserByID(bot, UserID, "What is the total number of healers for your crew? Please enter a number greater than 0.")
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      try:
        NrOfHealers = int(response.content)
        if NrOfHealers <= 0:
          NrOfHealers = None
          await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number greater than 0.")
          continue
      except:
        await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
        continue
      return NrOfHealers
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
      return

# Helper function to get users' role input
async def GetOrganizerRoleID(bot, message, UserID, NrOfTanks, NrOfDps, NrOfHealers):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  RoleName = None
  while not RoleName:
    try:
      await DMHelper.DMUserByID(bot, UserID, "Next, which role (tank/dps/healer) do you intend to play as within the crew?")
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
      return

    try:
      RoleID = await RoleHelper.GetRoleID(response.content.lower())
    except:
      await DMHelper.DMUserByID(bot, UserID, "Invalid role, please enter a valid role, you can call !roles in the servers Gyoshin channel to have available roles sent to this DM.")
      continue

    try:
      if response.content.lower() == "tank":
        if NrOfTanks <= 0:
          await DMHelper.DMUserByID(bot, UserID, "You have entered the role of tank, number of tanks must be greater than 0 for you to pick this role. Please pick a different role.")
        else:
          RoleName = response.content.lower()
          return RoleID
      elif response.content.lower() == "dps":
        if NrOfDps <= 0:
          await DMHelper.DMUserByID(bot, UserID, "You have entered the role of dps, number of dps must be greater than 0 for you to pick this role. Please pick a different role.")
        else:
          RoleName = response.content.lower()
          return RoleID
      elif response.content.lower() == "healer":
        if NrOfHealers <= 0:
          await DMHelper.DMUserByID(bot, UserID, "You have entered the role of healer, number of healers must be greater than 0 for you to pick this role. Please pick a different role.")
        else:
          RoleName = response.content.lower()
          return RoleID
      else:
        pass
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong checking the role and number of slots available.")
      return

# Helper function to get run status to set
async def GetRunStatusToSet(NrOfPlayers):
  if NrOfPlayers == 1:
    Status = "Formed"
  else:
    Status = "Forming"
  return Status

# Helper function to summarize and ask for confirmation
async def SummarizeRunInfoForConfirmation(bot, message, UserID, Name, DateTime, NrOfTanks, NrOfHealers, NrOfDps):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  Confirm = None
  while not Confirm:
    try:
      await DMHelper.DMUserByID(bot, UserID, f"Please confirm that you wish to create a crew with the following details (Y/N): \n**Description**: {Name}\n**Date:** {DateTime}\n**Number of Tanks:** {NrOfTanks}\n**Number of Healers:** {NrOfHealers}\n**Number of DPS:** {NrOfDps}")
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")

    if response.content in("Y","y","Yes","yes"):
      Confirm = "yes"
      return Confirm
    if response.content in("N","n","No","no"):
      Confirm = "no"
      return Confirm
    if response.content not in ("Y","y","Yes","yes","N","n","No","no"):
      continue

# Helper function to create the run
async def CreateRun(bot, message, UserID, Name, Origin, sqldatetime, NrOfPlayers, NrOfTanks, NumberOfCurrentTanks, NrOfDps, NumberOfCurrentDps, NrOfHealers, NumberOfCurrentHealers, Status, ChannelID, RoleID, CreatorDisplay, DateTime):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    c.execute("SELECT Name FROM Raids WHERE Origin = (?) and Name = (?) and Date = (?)", (Origin, Name, sqldatetime))
    row = c.fetchone()
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining run information")
    conn.close()
    return

  if row:
    await DMHelper.DMUserByID(bot, UserID, "There is already a run with the same description and time as your request, if making a party for the same event, please add \"Party 2\" for example to the description")
    conn.close()
    return

  try:
    c.execute("INSERT INTO Raids (Name, Origin, Date, OrganizerUserID, NrOfPlayersRequired, NrOfPlayersSignedUp, NrOfTanksRequired, NrOfTanksSignedUp, NrOfDpsRequired, NrOfDpsSignedUp, NrOfHealersRequired, NrOfHealersSignedUp, Status, ChannelID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (Name, Origin, sqldatetime, UserID, NrOfPlayers, 1, NrOfTanks, NumberOfCurrentTanks, NrOfDps, NumberOfCurrentDps, NrOfHealers, NumberOfCurrentHealers, Status, ChannelID))
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to create the run.")
    conn.close()
    return

  RaidID = c.lastrowid

  try:
    c.execute("INSERT INTO RaidMembers (Origin, UserID, RaidID, RoleID) VALUES (?, ?, ?, ?)", (Origin, UserID, RaidID, RoleID))
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong trying to add you as a member to this run.")
    conn.close()
    return

  try:
    TankIcon = await RoleIconHelper.GetTankIcon()
    DpsIcon = await RoleIconHelper.GetDpsIcon()
    HealerIcon = await RoleIconHelper.GetHealerIcon()
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving role icons")
    conn.close()
    return

  try:
    conn.commit()
    message = await message.channel.send(f"**Run:** {RaidID}\n**Description:** {Name}\n**Organizer:** {CreatorDisplay}\n**Date (UTC):** {DateTime}\n**Status:** {Status}\n{TankIcon} {NumberOfCurrentTanks}\/{NrOfTanks} {DpsIcon} {NumberOfCurrentDps}\/{NrOfDps} {HealerIcon} {NumberOfCurrentHealers}\/{NrOfHealers}",components=[[Button(style=ButtonStyle.blue, label="Tank", custom_id="tank_btn"),Button(style=ButtonStyle.red, label="DPS", custom_id="dps_btn"),Button(style=ButtonStyle.green, label="Healer", custom_id="healer_btn"),Button(style=ButtonStyle.grey, label="Rally", custom_id="rally_btn")],[Button(style=ButtonStyle.grey, label="Members", custom_id="members_btn"),Button(style=ButtonStyle.grey, label="Reserves", custom_id="reserves_btn"),Button(style=ButtonStyle.grey, label="Message members", custom_id="messageraidmembers_btn")],[Button(style=ButtonStyle.grey, label="Edit description", custom_id="editdesc_btn"),Button(style=ButtonStyle.grey, label="Reschedule", custom_id="reschedule_btn"),Button(style=ButtonStyle.red, label="Cancel", custom_id="cancel_btn")]])
    conn.close()
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong creating the run")
    conn.close()
    return
