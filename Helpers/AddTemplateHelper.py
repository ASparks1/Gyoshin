import sqlite3
import asyncio
import discord
from discord import ChannelType
from Helpers import DMHelper

async def NrOfPlayersAndConfirmSection(bot, message, Origin, UserID, TemplateName):
  def DMCheck(dm_message):
    return dm_message.channel.type == ChannelType.private and dm_message.author == message.author

  conn = sqlite3.connect('RaidPlanner.db')
  c = conn.cursor()

  NrOfPlayers = None
  while not NrOfPlayers:
    await DMHelper.DMUserByID(bot, UserID, "Please provide the amount of players required next.\n")
    try:
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      try:
        NrOfPlayers = int(response.content)
      except:
        await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
        continue
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a template.")
      conn.close()
      return

  NrOfTanks = None
  while not NrOfTanks:
    await DMHelper.DMUserByID(bot, UserID, "Please provide the amount of tanks required next.\n")
    try:
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      try:
        NrOfTanks = int(response.content)
      except:
        await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
        continue
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a template.")
      conn.close()
      return

  NrOfDps = None
  while not NrOfDps:
    await DMHelper.DMUserByID(bot, UserID, "Please provide the amount of dps required next.\n")
    try:
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      try:
        NrOfDps = int(response.content)
      except:
        await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
        continue
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a template.")
      conn.close()
      return

  NrOfHealers = None
  while not NrOfHealers:
    await DMHelper.DMUserByID(bot, UserID, "Please provide the amount of healers required next.\n")
    try:
      response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
      try:
        NrOfHealers = int(response.content)
      except:
        await DMHelper.DMUserByID(bot, UserID, "Please enter a valid number.")
        continue
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a template.")
      conn.close()
      return

  if NrOfPlayers == NrOfTanks + NrOfDps + NrOfHealers:
    await DMHelper.DMUserByID(bot, UserID, f"**Summary:**\nTemplate name: {TemplateName}\nNumber of players: {NrOfPlayers}\nNumber of tanks: {NrOfTanks}\nNumber of dps: {NrOfDps}\nNumber of healers{NrOfHealers}\nIs this correct (Y/N)?")
    try:
      CreateTemplate = None
      while not CreateTemplate:
        response = await bot.wait_for(event='message', timeout=60, check=DMCheck)
        if response.content in("Y","y","Yes","yes"):
          CreateTemplate = "yes"
          try:
            c.execute("INSERT INTO Templates (Origin, CreatorUserID, Name, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers) VALUES (?, ?, ?, ?, ?, ?, ?)", (Origin, UserID, TemplateName, NrOfPlayers, NrOfTanks, NrOfDps, NrOfHealers,))
            conn.commit()
            await DMHelper.DMUserByID(bot, UserID, "Template added succesfully.")
            conn.close()
            return
          except:
            await DMHelper.DMUserByID(bot, UserID, "Something went wrong adding the template.")
            conn.close()
            return
        elif response.content in("N","n","No","no"):
          CreateTemplate = "no"
          conn.close()
          return
        else:
          await DMHelper.DMUserByID(bot, UserID, "Invalid answer detected, please respond with yes or no.")
          continue
    except asyncio.TimeoutError:
      await DMHelper.DMUserByID(bot, UserID, "Your request has timed out, please call the command again from a server if you still wish to add a template.")
      conn.close()
      return
  else:
    await DMHelper.DMUserByID(bot, UserID, "The total amount of players required doesn't match the provided number of tanks, dps and healers provided.")
    conn.close()
    return
