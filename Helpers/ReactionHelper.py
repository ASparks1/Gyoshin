import sqlite3
import re
import asyncio
from datetime import datetime
from datetime import timedelta
from discord import ChannelType
from Helpers import DateTimeFormatHelper
from Helpers import DateTimeValidationHelper
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import NotificationHelper
from Helpers import DMHelper
from Helpers import RaidIDHelper
from Helpers import RoleHelper
from Helpers import RoleIconHelper
from Helpers import MessageHelper
from Helpers import MemberHelper

async def OnAddCancelReaction(message, bot, UserID):
  global CancelNotifications
  CancelNotifications = None
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Check if run still exists
  try:
    # Checks for waiting for dm replies
    def DMCheck(dm_message):
      return dm_message.channel.type == ChannelType.private and dm_message.author.id == UserID

    RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)

    if not RaidID:
      await DMHelper.DMUserByID(bot, UserID, f"I was not able to find run {RaidID}")
      conn.close()
      return
    c.execute("SELECT OrganizerUserID, Name, Date FROM Raids WHERE ID = (?)", (RaidID,))
    row = c.fetchone()
    Creator = row[0]
    RaidName = row[1]
    Date = row[2]
    LocalDate = await DateTimeFormatHelper.SqliteToLocalNoCheck(Date)

    if row:
      Origin = await OriginHelper.GetOrigin(message)

      if not Origin:
        return

      # Check that the user attempting to cancel the party is the party leader
      if UserID != Creator:
        await DMHelper.DMUserByID(bot, UserID, "Only the organizer of this run is allowed to cancel the run")
        conn.close()
        return

      # See if there are other members other than the leader, and send notifications to all
    try:
      c.execute("SELECT UserID FROM RaidMembers WHERE RaidID = (?) AND UserID != (?)", (RaidID, Creator,))
      UserIDs = c.fetchall()
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving raid members")
      conn.close()
      return

    try:
      if UserIDs:
        c.execute("SELECT UserID FROM RaidMembers WHERE RaidID = (?) AND UserID != (?)", (RaidID, Creator))
        RaidMembers = c.fetchall()
        CancelNotifications = await NotificationHelper.NotifyRaidMembers(message, RaidMembers)
    except:
      await DMHelper.DMUser(message, "Something went wrong retrieving raid members")
      conn.close()
      return

    try:
      GuildName = await OriginHelper.GetName(message)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining your nickname.")
      conn.close()
      return

    # Ask user to confirm the cancellation of the run
    CancelRun = None

    while not CancelRun:
      await DMHelper.DMUserByID(bot, UserID, f"Do you want to cancel the run {RaidName} on {LocalDate} in the {GuildName} server (Y/N)?")
      try:
        response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
        if response.content == "Y" or response.content == "y" or response.content == "Yes" or response.content == "yes":
          CancelRun = "yes"
        elif response.content == "N" or response.content == "n" or response.content == "No" or response.content == "no":
          CancelRun = "no"
        else:
          await DMHelper.DMUserByID(bot, UserID, "Invalid answer detected, please respond with Y/N")
          continue
      except asyncio.TimeoutError:
        await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again from the channel if you still want to cancel this run.")
        conn.close()
        return

    if CancelRun == "yes":
      c.execute("DELETE FROM RaidReserves WHERE RaidID = (?)", (RaidID,))
      c.execute("DELETE FROM RaidMembers WHERE RaidID = (?)", (RaidID,))
      c.execute("DELETE FROM Raids WHERE ID = (?)", (RaidID,))

      try:
        OrganizerDisplayName = await UserHelper.GetDisplayName(message, Creator, bot)
      except:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong resolving the organizers' display name")
        conn.close()
        return

      try:
        if CancelNotifications:
          await message.channel.send(f"{CancelNotifications}\n{OrganizerDisplayName} has cancelled the run {RaidName} on {LocalDate}.")
        elif not CancelNotifications:
          await message.channel.send(f"{OrganizerDisplayName} has cancelled the run {RaidName} on {LocalDate}.")

        conn.commit()
        await message.delete()
        conn.close()
        return
      except:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong cancelling the run")
        conn.close()
        return
    elif CancelRun == "no":
        conn.close()
        return
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong checking if this run still exists perhaps this run has been cancelled.")
    conn.close()
    return

async def OnAddRescheduleReaction(message, bot, UserID):
  global RescheduleNotifications
  RescheduleNotifications = None
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Checks for waiting for dm replies
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author.id == UserID

  # Get users' display name
  try:
    user = await bot.fetch_user(int(UserID))
    username = user.display_name
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining your nickname.")
    conn.close()
    return

  # Check if run still exists
  RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)

  if not RaidID:
    await DMHelper.DMUserByID(bot, UserID, f"I was not able to find run {RaidID}")
    conn.close()
    return

  # If run exists
  if RaidID:
    try:
      c.execute("SELECT Name, Date, OrganizerUserID FROM Raids WHERE ID = (?) AND NOT Status = 'Cancelled'", (RaidID,))
      row = c.fetchone()

      RaidName = row[0]
      OldDate = row[1]
      OrganizerUserID = row[2]
      LocalOldDate = await DateTimeFormatHelper.SqliteToLocal(message, OldDate)

      if OrganizerUserID != UserID:
        await DMHelper.DMUserByID(bot, UserID, "Only the organizer of this run is allowed to reschedule this run.")
        conn.close()
        return

    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining information for this run")
      conn.close()
      return

    try:
      GuildName = await OriginHelper.GetName(message)
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining the server information")
      conn.close()
      return

    # Get current datetime
    current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    await DMHelper.DMUserByID(bot, UserID, f"Hi {username}, please provide me the date to which you want to reschedule the run {RaidName} in the {GuildName} server in the dd-mm-yyyy hh:mm format.")

    if OldDate >= current_date:
      NewDate = None
      while not NewDate:
        try:
          response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
        except asyncio.TimeoutError:
          await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again from the channel if you still want to reschedule this run.")
          conn.close()
          return None

        # DateTime verification
        pattern = re.compile(r'((\d{2})-(\d{2})-(\d{4})) (\d{2}):(\d{2})')
        match = pattern.match(response.content)

        if not match:
          await DMHelper.DMUserByID(bot, UserID, "Invalid date and time detected, please use the dd-mm-yyyy hh:mm format")
          continue

        # Send datetime to function to format for SQL
        try:
          NewDate = response.content
          sqlitenewdate = await DateTimeFormatHelper.LocalToSqlite(message, NewDate)
        except:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong formatting the new date and time")
          conn.close()
          return

        if not sqlitenewdate or not NewDate:
          await DMHelper.DMUserByID(bot, UserID, "Something went wrong checking if date values are filled, please beware that you cannot reschedule to a date in the past.")
          continue

        if sqlitenewdate >= current_date:
          # Ask user to confirm the rescheduling of the run
          RescheduleRun = None
          while not RescheduleRun:
            await DMHelper.DMUserByID(bot, UserID, f"Do you want to reschedule the run {RaidName} from {LocalOldDate} to {NewDate} in the {GuildName} server (Y/N)?")
            try:
              response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
              if response.content == "Y" or response.content == "y" or response.content == "Yes" or response.content == "yes":
                RescheduleRun = "yes"
              elif response.content == "N" or response.content == "n" or response.content == "No" or response.content == "no":
                RescheduleRun = "no"
              else:
                await DMHelper.DMUserByID(bot, UserID, "Please enter a valid response of yes or no.")
                continue
            except asyncio.TimeoutError:
              await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again from the channel if you still want to reschedule this run.")
              conn.close()
              return

          if RescheduleRun == "yes":
            # Check if there are members signed up besides the organizer
            try:
              RescheduleNotifications = await MemberHelper.CheckForMembersBesidesOrganizer(bot, message, RaidID, UserID)
            except:
              await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving raid members")
              conn.close()
              return

            # Delete all raidmembers that are not the creator of the raid and reserves
            try:
              c.execute("DELETE FROM RaidMembers WHERE RaidID = (?) AND UserID != (?)", (RaidID, UserID,))
              c.execute("DELETE FROM RaidReserves WHERE RaidID = (?)", (RaidID,))
            except:
              conn.close()
              return

            # Get role of the Creator
            try:
              c.execute("SELECT RoleID FROM RaidMembers WHERE RaidID = (?) AND UserID = (?)", (RaidID, UserID,))
              row = c.fetchone()
            except:
              await DMHelper.DMUserByID(bot, UserID, "Something went wrong obtaining the role of the organizer")
              conn.close()
              return

            if not row:
              await DMHelper.DMUserByID(bot, UserID, "Unable to find role of the creator of this run")
              conn.close()
              return

            RoleID = row[0]

            if not RoleID:
              await DMHelper.DMUserByID(bot, UserID, "Unable to retrieve role id")
              conn.close()
              return

            RoleName = await RoleHelper.GetRoleName(RoleID)

            if not RoleName:
              await DMHelper.DMUserByID(bot, UserID, "Unable to resolve role name")
              conn.close()
              return

            # Update Raids table
            if RoleName == 'tank':
              try:
                c.execute("Update Raids SET Date = (?), NrOfPlayersSignedUp = (?), NrOfTanksSignedUp = (?), NrOfDpsSignedUp = (?), NrOfHealersSignedUp = (?), Status = 'Forming' WHERE ID = (?)", (sqlitenewdate, 1, 1, 0, 0, RaidID,))
                conn.commit()
              except:
                await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of players and tanks")
                conn.close()
                return

            if RoleName == 'dps':
              try:
                c.execute("Update Raids SET Date = (?), NrOfPlayersSignedUp = (?), NrOfTanksSignedUp = (?), NrOfDpsSignedUp = (?), NrOfHealersSignedUp = (?), Status = 'Forming' WHERE ID = (?)", (sqlitenewdate, 1, 0, 1, 0, RaidID,))
                conn.commit()
              except:
                await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of players and dps")
                conn.close()
                return

            if RoleName == 'healer':
              try:
                c.execute("Update Raids SET Date = (?), NrOfPlayersSignedUp = (?), NrOfTanksSignedUp = (?), NrOfDpsSignedUp = (?), NrOfHealersSignedUp = (?), Status = 'Forming' WHERE ID = (?)", (sqlitenewdate, 1, 0, 0, 1, RaidID,))
                conn.commit()
              except:
                await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the number of players and healers")
                conn.close()
                return

            try:
              conn.commit()
              UserName = await UserHelper.GetDisplayName(message, UserID, bot)

              if RescheduleNotifications:
                await message.channel.send(f"{RescheduleNotifications}\n{UserName} has rescheduled the run {RaidName} from {LocalOldDate} to {NewDate}, if you were signed up to this run please sign up again on the new date if you can.")
              elif not RescheduleNotifications:
                await message.channel.send(f"{UserName} has rescheduled the run {RaidName} from {LocalOldDate} to {NewDate}.")

              await message.delete()
              conn.close()
              return
            except:
              await DMHelper.DMUserByID(bot, UserID, "Something went wrong rescheduling the run")
              conn.close()
              return

async def OnAddRallyReaction(message, bot, UserID):
  global RallyNotifications
  RallyNotifications = None
  try:
    RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)

    if not RaidID:
      return
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong resolving the run number.")
  # Obtain server ID
  Origin = await OriginHelper.GetOrigin(message)

  if not Origin:
    return

  # Open database connection
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  # Find party through name and date for discord channel
  try:
    c.execute("SELECT ID, Date FROM Raids WHERE ID = (?)", (RaidID,))
    row = c.fetchone()
    RaidID = row[0]
    DateTime = row[1]
  except:
    await DMHelper.DMUserByID(bot, UserID, f"I was not able to find run {RaidID}.")
    conn.close()
    return

  # Check to see if user is a member of party.
  try:
    c.execute("SELECT ID FROM RaidMembers WHERE RaidID = (?) and UserID = (?)", (RaidID, UserID))
    row = c.fetchone()
    if not row:
      await DMHelper.DMUserByID(bot, UserID, f"Only members of run {RaidID} are allowed to rally the crew.")
      conn.close()
      return
  except:
    await DMHelper.DMUserByID(bot, UserID, f"Only members of run {RaidID} are allowed to rally the crew.")
    conn.close()
    return

  #check that the set time is within the next hour
  try:
    now = datetime.utcnow()
    DateTime = datetime.strptime(DateTime, "%Y-%m-%d %H:%M")
    TimeDifference = DateTime - now
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong checking dates.")
    conn.close()
    return

  if TimeDifference > timedelta(0) < timedelta(hours=2):
    #Complete Notifications
    try:
      c.execute("SELECT UserID FROM RaidMembers WHERE RaidID = (?) AND UserID != (?)", (RaidID, UserID))
      RaidMembers = c.fetchall()

      c.execute("SELECT RallyCount, Name FROM Raids WHERE ID = (?)", (RaidID,))
      row = c.fetchone()
      RallyCount = row[0]
      Name = row[1]

      if not RaidMembers:
          conn.close()
          await DMHelper.DMUserByID(bot, UserID, "There is nobody else in the crew to rally.")
          return
      if RaidMembers:
        RallyNotifications = await NotificationHelper.NotifyRaidMembers(message, RaidMembers)
        if RallyCount < 3:
          try:
            c.execute("UPDATE Raids SET RallyCount = RallyCount + 1 WHERE ID = (?)", (RaidID,))
          except:
            await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the rally count.")
            conn.close()
            return

          try:
            TimeTillRun = TimeDifference.seconds // 60
          except:
            await DMHelper.DMUserByID(bot, UserID, "Something went wrong calculating the time.")
            conn.close()
            return
          await message.channel.send(f"{RallyNotifications}\nGet ready crew! Only {TimeTillRun} minutes left until you assemble for {Name}!")
          conn.commit()
          conn.close()
        else:
          await DMHelper.DMUserByID(bot, UserID, "This crew has been rallied the maximum amount of 3 times already.")
          conn.close()
      else:
        await DMHelper.DMUserByID(bot, UserID, "Something went wrong retrieving the crew members.")
        conn.close()
        return
    except:
      await DMHelper.DMUserByID(bot, UserID, "Something went wrong with retrieving the names of the crew.")
      conn.close()
      return
  else:
    await DMHelper.DMUserByID(bot, UserID, "You can only rally the crew within an hour of the start time, it's too early to rally the crew for this run or the run has already started.")
    conn.close()
    return
  return

async def OnMemberReaction(message, bot):
  RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)

  if RaidID:
    Message = await MemberHelper.ListMembers(bot, message, 'Members', RaidID)
    return Message

async def OnReservesReaction(message, bot):
  RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)

  if RaidID:
    Message = await MemberHelper.ListMembers(bot, message, 'Reserves', RaidID)
    return Message

async def OnAddEditDescReaction(message, bot, UserID):
  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  try:
    # Checks for waiting for dm replies
    def DMCheck(dm_message):
      return dm_message.channel.type == ChannelType.private and dm_message.author.id == UserID

    RaidID = await RaidIDHelper.GetRaidIDFromMessage(message)

    if not RaidID:
      await DMHelper.DMUserByID(bot, UserID, f"I was not able to find run {RaidID}")
      conn.close()
      return

    c.execute("SELECT ID, Name, OrganizerUserID, Date FROM Raids WHERE ID = (?)", (RaidID,))
    row = c.fetchone()
    RaidID = row[0]
    RaidName = row[1]
    Creator = row[2]
    Date = row[3]
    CreatorDisplay = await UserHelper.GetDisplayName(message, UserID, bot)
    LocalDate = await DateTimeFormatHelper.SqliteToLocalNoCheck(Date)

    if row:
      if UserID != Creator:
        await DMHelper.DMUserByID(bot, UserID, "Only the organizer of this run is allowed to change the description of the run")
        conn.close()
        return

      await DMHelper.DMUserByID(bot, UserID, f"Please provide the new description for {RaidName} on {LocalDate}")
      try:
        response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      except asyncio.TimeoutError:
        await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again from the channel if you still want to cancel this run.")
        conn.close()
        return

      if response.content:
        EditDescription = None
        NewDescription = response.content

        while not EditDescription:
          await DMHelper.DMUserByID(bot, UserID, f"Do you want to change the description from {RaidName} to {NewDescription} on {LocalDate} (Y/N)?")
          try:
            response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
            if response.content == "Y" or response.content == "y" or response.content == "Yes" or response.content == "yes":
              EditDescription = "yes"
            elif response.content == "N" or response.content == "n" or response.content == "No" or response.content == "no":
              EditDescription = "no"
            else:
              await DMHelper.DMUserByID(bot, UserID, "Invalid answer detected, please respond with Y/N")
              continue
          except asyncio.TimeoutError:
            await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please click the button again from the channel if you still want to cancel this run.")
            conn.close()
            return

        if EditDescription == 'yes':
          try:
            c.execute("UPDATE Raids set Name = (?) WHERE ID = (?)", (NewDescription, RaidID,))
            conn.commit()
            await message.channel.send(f"{CreatorDisplay} has changed the description of run {RaidID} on {LocalDate} from {RaidName} to {NewDescription}.")
            UpdatedMessage = await MessageHelper.UpdateRaidInfoMessage(message, bot, UserID)
            await message.edit(content=UpdatedMessage)
            conn.close()
            return
          except:
            await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the description of this run 1")
            conn.close()
            return
  except:
    await DMHelper.DMUserByID(bot, UserID, "Something went wrong updating the description of this run 2")
    conn.close()
    return
