import sqlite3
import asyncio
from Helpers import OriginHelper
from Helpers import UserHelper
from Helpers import DMHelper
from discord import ChannelType

async def AddTemplate(message, bot):
  #Obtain origin of server of original !addrun command and display name of user for channel, and name for DM
  try:
    Origin = await OriginHelper.GetOrigin(message)
    UserID = message.author.id
    GuildName = await OriginHelper.GetName(message) 
    Creator = await UserHelper.GetUserID(message)
    CreatorDisplay = await UserHelper.GetDisplayName(message, Creator, bot)
  except:
     await DMHelper.DMUserByID(bot, UserID, f"Something went wrong when gathering server and user information.")
     return
  
  # Checks for waiting for dm replies
  def DMCheck(dm_message):
    return (dm_message.channel.type == ChannelType.private and dm_message.author == message.author)
    
  # Ask user for description of planned party/run, and wait for input
  await DMHelper.DMUserByID(bot, UserID, f"Hi {CreatorDisplay}, let's create a template in the {GuildName} server.\nFirst, give me the name of your template, please beware that spaces are not allowed in template names.\n")
  try:
    response = await bot.wait_for(event='message' ,timeout = 60, check= DMCheck)
  except asyncio.TimeoutError:
    await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a template.")
    return   

  TemplateName = response.content
  
  # Check if there already is a template with this name
  if TemplateName:
    try:
      conn = sqlite3.connect('RaidPlanner.db')
      c = conn.cursor()
      c.execute(f"SELECT ID FROM Templates WHERE Name = (?) AND Origin = (?)", (TemplateName, Origin,))
      row = c.fetchone()
      
      if row:
        await DMHelper.DMUserByID(bot, UserID, f"There already exists a template with the name {TemplateName} on the {GuildName} server")
        conn.close()
        return
    except:
      await DMHelper.DMUserByID(bot, UserID, f"Something went wrong checking if a template with the same name already exists on this server")
      conn.close()
      return
  
  # Create empty var for while loop until a valid number of players has been entered
  NrOfPlayers = None
  
  while not NrOfPlayers:
    await DMHelper.DMUserByID(bot, UserID, f"Please provide the amount of players required next.\n")
    try:
      response = await bot.wait_for(event='message' ,timeout = 60, check= DMCheck)
      try:
        NrOfPlayers = int(response.content)
      except:
        await DMHelper.DMUserByID(bot, UserID, f"Please enter a valid number.")
        continue
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, f"Your request has timed out, please call the command again from a server if you still wish to add a template.")
      conn.close()
      return
  
  # Create empty var for while loop until a valid number of tanks has been entered
  NrOfTanks = None
  
  while not NrOfTanks:
    await DMHelper.DMUserByID(bot, UserID, f"Please provide the amount of tanks required next.\n")
    try:
      response = await bot.wait_for(event='message' ,timeout = 60, check= DMCheck)
      try:
        NrOfTanks = int(response.content)
      except:
        await DMHelper.DMUserByID(bot, UserID, f"Please enter a valid number.")
        continue
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, f"Your request has timed out, please call the command again from a server if you still wish to add a template.")
      conn.close()
      return
  
  # Create empty var for while loop until a valid number of dps has been entered
  NrOfDps = None
  
  while not NrOfDps:
    await DMHelper.DMUserByID(bot, UserID, f"Please provide the amount of dps required next.\n")
    try:
      response = await bot.wait_for(event='message' ,timeout = 60, check= DMCheck)
      try:
        NrOfDps = int(response.content)
      except:
        await DMHelper.DMUserByID(bot, UserID, f"Please enter a valid number.")
        continue
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, f"Your request has timed out, please call the command again from a server if you still wish to add a template.")
      conn.close()
      return
  
  # Create empty var for while loop until a valid number of dps has been entered
  NrOfHealers = None
  
  while not NrOfHealers:
    await DMHelper.DMUserByID(bot, UserID, f"Please provide the amount of healers required next.\n")
    try:
      response = await bot.wait_for(event='message' ,timeout = 60, check= DMCheck)
      try:
        NrOfHealers = int(response.content)
      except:
        await DMHelper.DMUserByID(bot, UserID, f"Please enter a valid number.")
        continue
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, f"Your request has timed out, please call the command again from a server if you still wish to add a template.")
      conn.close()
      return
  
  
  # Check if the role numbers match the total numbers
  if NrOfPlayers == NrOfTanks + NrOfDps + NrOfHealers:
    await DMHelper.DMUserByID(bot, UserID, f"**Summary:**\nTemplate name: {TemplateName}\nNumber of players: {NrOfPlayers}\nNumber of tanks: {NrOfTanks}\nNumber of dps: {NrOfDps}\nNumber of healers{NrOfHealers}\nIs this correct (Y/N)?")
    try:
      CreateTemplate = None
      while not CreateTemplate:
        response = await bot.wait_for(event='message' ,timeout = 60, check= DMCheck)
        if response.content == "Y" or response.content == "y" or response.content == "Yes" or response.content == "yes":
          CreateTemplate = "yes"
          try:
            c.execute(f"INSERT INTO Templates (Origin, CreatorUserID, Name, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES (?, ?, ?, ?, ?, ?, ?)", (Origin, UserID, TemplateName, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers,))
            conn.commit()
            await DMHelper.DMUserByID(bot, UserID, f"Template added succesfully.")
            conn.close()
            return
          except:
            await DMHelper.DMUserByID(bot, UserID, f"Something went wrong adding the template.")
            conn.close()
            return  
        elif response.content == "N" or response.content == "n" or response.content == "No" or response.content == "no":
          CreateTemplate = "no"
          conn.close()
          return
        else:
          await DMHelper.DMUserByID(bot, UserID, f"Invalid answer detected, please respond with yes or no.")
          continue
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, f"Your request has timed out, please call the command again from a server if you still wish to add a template.")
      conn.close()
      return
  else:
    await DMHelper.DMUserByID(bot, UserID, f"The total amount of players required doesn't match the provided number of tanks, dps and healers provided.")