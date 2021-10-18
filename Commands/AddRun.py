import sqlite3
import re
import asyncio
from discord_components import DiscordComponents, Button, ButtonStyle
from Helpers import DateTimeFormatHelper
from Helpers import RoleHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import RoleIconHelper
from Helpers import DMHelper
from Helpers import ReactionHelper
from Helpers import RaidIDHelper
from Helpers import ButtonInteractionHelper
from discord import ChannelType
from Commands import Templates


async def AddRunInDM(message, bot):

  DateTime = None
  RoleName = None
  UsingTemplate = None

  try:
    Origin = await OriginHelper.GetOrigin(message)
    GuildName = await OriginHelper.GetName(message)
    UserID = message.author.id
    CreatorDisplay = await UserHelper.GetDisplayName(message, UserID, bot)
    ChannelID = message.channel.id
  except:
     await DMHelper.DMUserByID(bot, UserID, "Something went wrong when gathering server and user information.")
     return

  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  await DMHelper.DMUserByID(bot, UserID, f"Hi {CreatorDisplay}, let's get you forming your crew in {GuildName}.\nFirst, give me a brief description for your crew, e.g. 'Friday Night Alliance Raid'.\n")
  try:
    response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
  except asyncio.TimeoutError:
    await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
    return

  Name = response.content

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
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong saving the date & time")
      return

  await Templates.GetTemplates(message)

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
        return

      if response.content == "Y" or response.content == "y" or response.content == "Yes" or response.content == "yes":
        UsingTemplate = "yes"
      elif response.content == "N" or response.content == "n" or response.content == "No" or response.content == "no":
        UsingTemplate = "no"
      else:
        await DMHelper.DMUserByID(bot, UserID, "Please enter a valid response of 'yes' or 'no'.")
  else:
    UsingTemplate = "no"

  if UsingTemplate == 'yes':
    template_completion = False
    while not template_completion:
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
        conn.close()
        continue

      try:
        NrOfPlayers = row[0]
        NrOfTanks = row[1]
        NrOfDps = row[2]
        NrOfHealers = row[3]
      except:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining the player and/or role numbers from the template, please try again.")
        conn.close()
        continue

      template_completion = True

  else:
    variable_completion = False
    while not variable_completion:
      PlayerLoop = False
      TankLoop = False
      HealerLoop = False
      DpsLoop = False

      while not PlayerLoop:
        try:
          await DMHelper.DMUserByID(bot, UserID, "What is the total number of players for your crew? Please enter a number greater than 0.")
          response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
          try:
            NrOfPlayers = int(response.content)
          except:
            await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
            continue
        except asyncio.TimeoutError:
          await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
          conn.close()
          return

        if NrOfPlayers <= 0:
          await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number greater than 0.")
          continue

        PlayerLoop = True

      while not TankLoop:
        try:
          await DMHelper.DMUserByID(bot, UserID, "What is the total number of tanks for your crew? Please enter a number equal or greater than 0.")
          response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
          try:
            NrOfTanks = int(response.content)
          except:
            await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
            continue
        except asyncio.TimeoutError:
          await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
          return

        TankLoop = True

      while not HealerLoop:
        try:
          await DMHelper.DMUserByID(bot, UserID, "What is the total number of healers for your crew? Please enter a number equal or greater than 0.")
          response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
          try:
            NrOfHealers = int(response.content)
          except:
            await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
            continue
        except asyncio.TimeoutError:
          await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
          conn.close()
          return

        HealerLoop = True

      while not DpsLoop:
        try:
          await DMHelper.DMUserByID(bot, UserID, "What is the total number of dps for your crew? Please enter a number equal or greater than 0.")
          response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
          try:
            NrOfDps = int(response.content)
          except:
            await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
            continue
        except asyncio.TimeoutError:
          await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
          conn.close()
          return

        DpsLoop = True

      if NrOfPlayers != NrOfTanks + NrOfDps + NrOfHealers:
        await DMHelper.DMUserByID(bot, UserID, "Please ensure the total of each role equals the total number of players required.")
        continue

      variable_completion = True

  while not RoleName:
    try:
      await DMHelper.DMUserByID(bot, UserID, "Next, which role (tank/dps/healer) do you intend to play as within the crew?")
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")
      conn.close()
      return

    try:
      RoleID = await RoleHelper.GetRoleID(response.content.lower())
    except:
      await DMHelper.DMUserByID(bot, UserID, "Invalid role, please enter a valid role, you can call !roles in the servers Gyoshin channel to have available roles sent to this DM.")
      continue

    NumberOfCurrentTanks = 0
    NumberOfCurrentDps = 0
    NumberOfCurrentHealers = 0

    try:
      if response.content.lower() == "tank":
        if NrOfTanks <= 0:
          await DMHelper.DMUserByID(bot, UserID, "You have entered the role of tank, number of tanks must be greater than 0 for you to pick this role. Please pick a different role.")
        else:
          NumberOfCurrentTanks = 1
          RoleName = response.content.lower()
      elif response.content.lower() == "dps":
        if NrOfDps <= 0:
          await DMHelper.DMUserByID(bot, UserID, "You have entered the role of dps, number of dps must be greater than 0 for you to pick this role. Please pick a different role.")
        else:
          NumberOfCurrentDps = 1
          RoleName = response.content.lower()
      elif response.content.lower() == "healer":
        if NrOfHealers <= 0:
          await DMHelper.DMUserByID(bot, UserID, "You have entered the role of healer, number of healers must be greater than 0 for you to pick this role. Please pick a different role.")
        else:
          NumberOfCurrentHealers = 1
          RoleName = response.content.lower()
      else:
        pass
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong checking the role and number of slots available.")
      conn.close()
      return

  if NrOfPlayers == 1:
    Status = "Formed"
  else:
    Status = "Forming"

  final_confirmation = False
  while not final_confirmation:
    try:
      await DMHelper.DMUserByID(bot, UserID, f"Please confirm that you wish to create a crew with the following details (Y/N): \n**Description**: {Name}\n**Date:** {DateTime}\n**Number of Tanks:** {NrOfTanks}\n**Number of Healers:** {NrOfHealers}\n**Number of DPS:** {NrOfDps}")
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a run.")

    if response.content == "Y" or response.content == "y" or response.content == "Yes" or response.content == "yes":
      final_confirmation = True
    elif response.content == "N" or response.content == "n" or response.content == "No" or response.content == "no":
      await DMHelper.DMUserByID(bot, UserID, "Your request to create a crew has been cancelled, please call the command again in the relevant channel if you wish to try again.")
      conn.close()
      return
    else:
      continue

  try:
    c.execute("SELECT Name FROM Raids WHERE Origin = (?) and Name = (?) and Date = (?)", (Origin, Name, sqldatetime))

    row = c.fetchone()
  except:
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
    message = await message.channel.send(f"**Run:** {RaidID}\n**Description:** {Name}\n**Organizer:** {CreatorDisplay}\n**Date (UTC):** {DateTime}\n**Status:** {Status}\n{TankIcon} {NumberOfCurrentTanks}\/{NrOfTanks} {DpsIcon} {NumberOfCurrentDps}\/{NrOfDps} {HealerIcon} {NumberOfCurrentHealers}\/{NrOfHealers}",components=[[Button(style=ButtonStyle.blue, label="Tank", custom_id="tank_btn"),Button(style=ButtonStyle.red, label="DPS", custom_id="dps_btn"),Button(style=ButtonStyle.green, label="Healer", custom_id="healer_btn"),Button(style=ButtonStyle.grey, label="Rally", custom_id="rally_btn")],[Button(style=ButtonStyle.grey, label="Members", custom_id="members_btn"),Button(style=ButtonStyle.grey, label="Reserves", custom_id="reserves_btn")],[Button(style=ButtonStyle.grey, label="Edit description", custom_id="editdesc_btn"),Button(style=ButtonStyle.grey, label="Reschedule", custom_id="reschedule_btn"),Button(style=ButtonStyle.red, label="Cancel", custom_id="cancel_btn")]])
    conn.close()
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong creating the run")
    conn.close()
    return
